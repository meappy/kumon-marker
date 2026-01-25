## [0.6.2](https://github.com/meappy/kumon-marker/compare/v0.6.1...v0.6.2) (2026-01-25)


### Bug Fixes

* improve Google Drive file matching and add validation caching ([9ea2a50](https://github.com/meappy/kumon-marker/commit/9ea2a5040edb66ff46dcac9c4b6807c0c86a7d6f))

## [0.6.1](https://github.com/meappy/kumon-marker/compare/v0.6.0...v0.6.1) (2026-01-25)


### Bug Fixes

* session cookie secure flag and OAuth scope mismatch ([91011cd](https://github.com/meappy/kumon-marker/commit/91011cdf2545f301cbcff4258a444747e393dd8b))

# [0.6.0](https://github.com/meappy/kumon-marker/compare/v0.5.3...v0.6.0) (2026-01-19)


### Features

* add christopher.xj.wong@gmail.com to allowed users ([f102680](https://github.com/meappy/kumon-marker/commit/f102680dd93da8b54f68003d197d6f0cbe7364ce))

## [0.5.3](https://github.com/meappy/kumon-marker/compare/v0.5.2...v0.5.3) (2026-01-19)


### Bug Fixes

* prevent HTTPException from being caught by generic exception handler ([28346dd](https://github.com/meappy/kumon-marker/commit/28346ddc195c44f08419e2e07460550ce21ea7bb))

## [0.5.2](https://github.com/meappy/kumon-marker/compare/v0.5.1...v0.5.2) (2026-01-19)


### Bug Fixes

* improve error messages for Google Drive connection issues ([8eaee17](https://github.com/meappy/kumon-marker/commit/8eaee17958bd2c0684667ee031e7e969ab9dfe71))

## [0.5.1](https://github.com/meappy/kumon-marker/compare/v0.5.0...v0.5.1) (2026-01-18)


### Bug Fixes

* run Google Drive scan in thread pool to prevent health check timeouts ([dc75597](https://github.com/meappy/kumon-marker/commit/dc75597ffd8eb7b3b2a1f128c64bad9ab1211e6f))

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.12...v0.5.0) (2026-01-18)


### Features

* add graceful shutdown for worker to complete in-progress jobs ([7ec2a64](https://github.com/meappy/kumon-marker/commit/7ec2a64601dce2e15879aa52b63241353edaace7))

## [0.4.12](https://github.com/meappy/kumon-marker/compare/v0.4.11...v0.4.12) (2026-01-18)


### Bug Fixes

* improve error handling for Google Drive API responses ([ead4e5c](https://github.com/meappy/kumon-marker/commit/ead4e5cd7eddcfede22714ac03502858cd6186b3))

## [0.4.11](https://github.com/meappy/kumon-marker/compare/v0.4.10...v0.4.11) (2026-01-18)


### Bug Fixes

* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([5d5eb87](https://github.com/meappy/kumon-marker/commit/5d5eb876128af93777dc329ca3336408b69f7c13))

## [0.4.10](https://github.com/meappy/kumon-marker/compare/v0.4.9...v0.4.10) (2026-01-18)


### Bug Fixes

* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([c5feda2](https://github.com/meappy/kumon-marker/commit/c5feda2ebe5ae8e075db653e37c16b071d7ff14e))

## [0.4.9](https://github.com/meappy/kumon-marker/compare/v0.4.8...v0.4.9) (2026-01-18)


### Bug Fixes

* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([89f1355](https://github.com/meappy/kumon-marker/commit/89f135514c66600de9d5510ce4b50c7c981a5f40))

## [0.4.8](https://github.com/meappy/kumon-marker/compare/v0.4.7...v0.4.8) (2026-01-18)


### Bug Fixes

* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([30343c7](https://github.com/meappy/kumon-marker/commit/30343c74cf5fc97103559c82334b46ef9bdd499a))

## [0.4.7](https://github.com/meappy/kumon-marker/compare/v0.4.6...v0.4.7) (2026-01-18)


### Bug Fixes

* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([9d9e243](https://github.com/meappy/kumon-marker/commit/9d9e2433f530933759768e568ff35f78658f62f0))

## [0.4.6](https://github.com/meappy/kumon-marker/compare/v0.4.5...v0.4.6) (2026-01-18)


### Bug Fixes

* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([8a1a2b6](https://github.com/meappy/kumon-marker/commit/8a1a2b6e221a30551fdb79bc02b9dc89f4e743ad))

## [0.4.5](https://github.com/meappy/kumon-marker/compare/v0.4.4...v0.4.5) (2026-01-18)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([a233e5d](https://github.com/meappy/kumon-marker/commit/a233e5d715c4f86c0c29fe8afdd0c6d96b67ed43))

## [0.4.4](https://github.com/meappy/kumon-marker/compare/v0.4.3...v0.4.4) (2026-01-18)


### Bug Fixes

* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([21e8831](https://github.com/meappy/kumon-marker/commit/21e88311b4478ba11a7bcb9f71e0766ba0f0e8bb))

## [0.4.3](https://github.com/meappy/kumon-marker/compare/v0.4.2...v0.4.3) (2026-01-18)


### Bug Fixes

* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([eb34da5](https://github.com/meappy/kumon-marker/commit/eb34da581389b89046116a8c3fec5ceb4e4f08e8))

## [0.4.2](https://github.com/meappy/kumon-marker/compare/v0.4.1...v0.4.2) (2026-01-18)


### Bug Fixes

* capture semantic-release output for Docker build trigger ([e6ff88c](https://github.com/meappy/kumon-marker/commit/e6ff88cd217801a4e0b0965db30812fa636f3ad1))

## [0.4.1](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.4.1) (2026-01-18)


### Bug Fixes

* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([02a2340](https://github.com/meappy/kumon-marker/commit/02a2340019c7ab9a3ff812c111bf421f1a187433))

# [0.4.0](https://github.com/meappy/kumon-marker/compare/v0.3.0...v0.4.0) (2026-01-17)


### Features

* auto-deploy branches via Argo CD ([3269e44](https://github.com/meappy/kumon-marker/commit/3269e44aca665f1d9ddd99d86fb164cdf1db60d9))

# [0.3.0](https://github.com/meappy/kumon-marker/compare/v0.2.8...v0.3.0) (2026-01-17)


### Features

* add GitOps CI/CD with Semantic Release and Argo CD ([3920d2b](https://github.com/meappy/kumon-marker/commit/3920d2b18dce4aab1365e26fe89859d252c1ec61))
