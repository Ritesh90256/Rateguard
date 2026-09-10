import http from "k6/http";
import { check, sleep } from "k6";
import { Counter, Rate } from "k6/metrics";


const allowedRequests = new Counter("allowed_requests");
const deniedRequests = new Counter("denied_requests");
const invalidResponses = new Rate("invalid_responses");


const baseUrl = __ENV.BASE_URL || "http://127.0.0.1:8000";


const clients = [
    {
        id: "Client-A",
        tier: "free",
        algorithm: "token_bucket",
    },
    {
        id: "Client-B",
        tier: "pro",
        algorithm: "sliding_window_log",
    },
    {
        id: "Client-C",
        tier: "enterprise",
        algorithm: "sliding_window_counter",
    },
];


const scenarios = {
    sustained: {
        executor: "constant-vus",
        vus: 10,
        duration: "30s",
    },

    burst: {
        executor: "ramping-vus",
        startVUs: 5,
        stages: [
            {
                duration: "5s",
                target: 50,
            },
            {
                duration: "5s",
                target: 100,
            },
            {
                duration: "5s",
                target: 10,
            },
        ],
        gracefulRampDown: "2s",
    },
};


const selectedScenario = __ENV.SCENARIO || "sustained";


export const options = {
    scenarios: {
        load_test: scenarios[selectedScenario] || scenarios.sustained,
    },

    thresholds: {
        http_req_failed: ["rate<0.01"],
        http_req_duration: [
            "p(50)<100",
            "p(95)<250",
            "p(99)<500",
        ],
        invalid_responses: ["rate<0.01"],
    },
};


export default function () {
    const client = clients[(__VU - 1) % clients.length];

    const response = http.post(
        `${baseUrl}/check`,
        JSON.stringify({
            client_id: client.id,
        }),
        {
            headers: {
                "Content-Type": "application/json",
            },

            tags: {
                tier: client.tier,
                algorithm: client.algorithm,
            },
        }
    );


    const bodyIsValid = response.status === 200 &&
        typeof response.json().allowed === "boolean";


    check(response, {
        "status is 200": (response) => response.status === 200,
        "response contains allowed": () => bodyIsValid,
    });


    invalidResponses.add(!bodyIsValid);


    if (response.status === 200 && bodyIsValid) {
        const allowed = response.json().allowed;

        if (allowed) {
            allowedRequests.add(1);
        } else {
            deniedRequests.add(1);
        }
    }


    sleep(0.1);
}