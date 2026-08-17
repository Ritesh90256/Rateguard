# RateGuard

RateGuard is a standalone, horizontally scalable rate limiting service built with FastAPI and Redis.

It provides a centralized rate-limiting layer that client applications can sit behind, with support for multiple rate-limiting algorithms and distributed state.

## Features

- Token Bucket rate limiting
- Sliding Window Log rate limiting
- Sliding Window Counter rate limiting
- Redis-backed distributed state
- Per-client / API-key rate limits
- Tier-based client configuration
- Horizontally scalable service instances
- Load balancing with nginx
- Hot-reloadable configuration
- Load testing and performance benchmarking

## Architecture

```text
Client Applications
        |
        v
      nginx
        |
   +----+----+
   |    |    | 
   v    v    v 
 RG-1  RG-2  RG-3  ... RateGuard instances
   |    |    |
   +----+----+
        |
        v
      Redis
