# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([3e151e7](https://github.com/meappy/kumon-marker/commit/3e151e7a4179bd022eb53b957cb20e2f556be252))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([185001e](https://github.com/meappy/kumon-marker/commit/185001ede41dc8b68e988fb57b8cc9f4aaed0c0a))
* add quick text-layer check to filter non-Kumon PDFs ([de4586c](https://github.com/meappy/kumon-marker/commit/de4586c13cb1a5a47e64e28d307338f504ee6dab))
* capture semantic-release output for Docker build trigger ([8205c2e](https://github.com/meappy/kumon-marker/commit/8205c2e23adbbbaf52924b0709a6d52721c9544f))
* clear validation cache when refresh is clicked ([68154fc](https://github.com/meappy/kumon-marker/commit/68154fcdd8a21d48c58c3933c3c257cc289c3841))
* correct sheet_id matching logic in GDriveModal ([f469a03](https://github.com/meappy/kumon-marker/commit/f469a0322f4b6fc23f69127f348e4efe51ef8559))
* extract sheet_id from PDF text layer during refresh ([1931b4a](https://github.com/meappy/kumon-marker/commit/1931b4aa8d332c527bb4672ba15a34e264f6df11))
* force revalidation when refresh is clicked ([fc6bff6](https://github.com/meappy/kumon-marker/commit/fc6bff68c6604aa0c91aac2a7e120bcb56e0f50b))
* improve error handling for Google Drive API responses ([d383b1c](https://github.com/meappy/kumon-marker/commit/d383b1c57dc690b6049b533011002619cbe18480))
* improve error messages for Google Drive connection issues ([be13cfb](https://github.com/meappy/kumon-marker/commit/be13cfbf6e284bdf7d74e93ec1a8170c1b077f57))
* improve Google Drive file matching and add validation caching ([4c82288](https://github.com/meappy/kumon-marker/commit/4c82288873a10e05d36c00267819a0cf6b4756d2))
* improve OCR accuracy with image pre-processing ([117f09a](https://github.com/meappy/kumon-marker/commit/117f09aa37bb88e70015e25fd8415a37e26479a4))
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([2893278](https://github.com/meappy/kumon-marker/commit/28932780c71dd11f534965e88c9c2102ce594b1b))
* improve sheet ID and topic extraction from worksheets ([ff666cd](https://github.com/meappy/kumon-marker/commit/ff666cd00305c0aaafb54d78debb09c87338302a))
* log model name alongside vision provider in worker ([cda9a5e](https://github.com/meappy/kumon-marker/commit/cda9a5eaafb24576b3bc2b5f73ea030efc2a24e1))
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([435e4a8](https://github.com/meappy/kumon-marker/commit/435e4a89b3461c72808c3a6aa792b3bdec82f77f))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([95f8c06](https://github.com/meappy/kumon-marker/commit/95f8c06521e95bd4d60d7098e57e080b6fc28ef8))
* prevent HTTPException from being caught by generic exception handler ([e3bb523](https://github.com/meappy/kumon-marker/commit/e3bb5230859550a4dbcefcf01306ad1ea7d5d9a1))
* reduce memory requests to 512Mi for scheduling ([f8651aa](https://github.com/meappy/kumon-marker/commit/f8651aaf4658db25842cd9aea9d89784c7019d85))
* refresh now re-extracts sheet_ids instead of using cache ([cca27f5](https://github.com/meappy/kumon-marker/commit/cca27f5ffc2b740d60f308bf0d7c11684c13d59a))
* regex pattern now matches uppercase A/B suffix after .upper() ([2f529e3](https://github.com/meappy/kumon-marker/commit/2f529e3dff8bc4f3ec60995efa7e35272de7c76e))
* remove unused import ([699dbf1](https://github.com/meappy/kumon-marker/commit/699dbf1131d9ada7c55ef1956d8d1819c72431d9))
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([722a535](https://github.com/meappy/kumon-marker/commit/722a535cc04b87e3e3220e6d327f5728a247523a))
* run Google Drive scan in thread pool to prevent health check timeouts ([ba2de71](https://github.com/meappy/kumon-marker/commit/ba2de71c72328bfbfa54cf86922aa0424be1c0e5))
* separate refresh (fast) from revalidate (slow) for GDrive files ([7e22b40](https://github.com/meappy/kumon-marker/commit/7e22b404d2f8d2d32c36194b0b3ec53de21b06d3))
* session cookie secure flag and OAuth scope mismatch ([ba14bbd](https://github.com/meappy/kumon-marker/commit/ba14bbdcce62a5c9cf0cf2950c89c5bdbb00ceec))
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([46b4d37](https://github.com/meappy/kumon-marker/commit/46b4d37e40f8821afebaafe5e1054d8fb96880c3))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon ([ef27a79](https://github.com/meappy/kumon-marker/commit/ef27a794f54337a176a85959d4dfbae88a4bd0d8))
* store PKCE code_verifier in signed cookie for OAuth callback ([7d7084e](https://github.com/meappy/kumon-marker/commit/7d7084e2803c4db9fb692a47ce228f2639470ed4))
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([266c94c](https://github.com/meappy/kumon-marker/commit/266c94cccb2515ad3792cb2bab76b15d1c52dfc7))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([f48ca7f](https://github.com/meappy/kumon-marker/commit/f48ca7fd0a4ccfca342e2d1311bf34bd7e57c002))
* use filename for sheet_id extraction, simplify OCR ([e78d2d1](https://github.com/meappy/kumon-marker/commit/e78d2d1e3b87e78e845d3b020b011527e5626840))
* use vision model instead of unreliable Tesseract OCR for validation ([193df98](https://github.com/meappy/kumon-marker/commit/193df981c9e06a2f80f3aec53523a1c0bf391693))
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([7f14dfe](https://github.com/meappy/kumon-marker/commit/7f14dfe7ce0088f5d2d6138ca8cd450c83398636))


### Features

* add branding assets and update README ([0605d7b](https://github.com/meappy/kumon-marker/commit/0605d7bc14f3d3ec716343bcf53e59eb3b64a4dc))
* add graceful shutdown for worker to complete in-progress jobs ([0f71362](https://github.com/meappy/kumon-marker/commit/0f713628675270b2136111ef4dd531590b31d53e))
* add group-by-student option for worksheet list ([62e9581](https://github.com/meappy/kumon-marker/commit/62e9581dcbd381da9c1f334bd4ebaabce803ba53))
* add ingress template and enable for production domain ([647fc61](https://github.com/meappy/kumon-marker/commit/647fc6188706fda5b7b522381f72281f84950a53))
* add pre-commit hook for branch protection and linting ([93a3dc0](https://github.com/meappy/kumon-marker/commit/93a3dc0c5fa94758129ee90f9723c5ec9276b5f5))
* add Revalidate button to GDrive modal ([6aa4f4a](https://github.com/meappy/kumon-marker/commit/6aa4f4a21e46843c3de90acf251f6c5d39dbaad3))
* add user to allowed users list ([04b264e](https://github.com/meappy/kumon-marker/commit/04b264e5fc178d4e9ad0eddd7e9d107a1f7d1b55))
* dual secret support and ArgoCD multi-source secrets repo ([1610065](https://github.com/meappy/kumon-marker/commit/1610065fed9d3da706883e2ddc60d471b6843d0b))
* move allowed users to private secrets repo ([d7ef576](https://github.com/meappy/kumon-marker/commit/d7ef576edd3edd3eed891b0945d0772133524fa5))
* move ingress host and internal IPs to private secrets repo ([c6fd45d](https://github.com/meappy/kumon-marker/commit/c6fd45da12263bb46a996d9fdfeda88236ce29a2))
* refactor to pluggable multi-provider architecture ([31c5c2c](https://github.com/meappy/kumon-marker/commit/31c5c2cee1c636e15912bcb96316ee4a6c637589))
* switch from Claude CLI to API mode ([fed6fab](https://github.com/meappy/kumon-marker/commit/fed6fab01e765844a0bdb62eaf913458007e8ae3))
* use claude-opus-4-6 model for worksheet analysis ([e9dd98c](https://github.com/meappy/kumon-marker/commit/e9dd98c243b8d0a85b48e14f8c47737c10d9eec0))
* use Tesseract OCR for sheet ID extraction ([1b9c413](https://github.com/meappy/kumon-marker/commit/1b9c413b618b7138ee0f07179fcf4d3d03f34509))


### Performance Improvements

* extract sheet_id from filename first, skip download if valid ([6a801e6](https://github.com/meappy/kumon-marker/commit/6a801e651c8d4495da8b2db5e53c19a162fa164a))

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([3e151e7](https://github.com/meappy/kumon-marker/commit/3e151e7a4179bd022eb53b957cb20e2f556be252))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([185001e](https://github.com/meappy/kumon-marker/commit/185001ede41dc8b68e988fb57b8cc9f4aaed0c0a))
* add quick text-layer check to filter non-Kumon PDFs ([de4586c](https://github.com/meappy/kumon-marker/commit/de4586c13cb1a5a47e64e28d307338f504ee6dab))
* capture semantic-release output for Docker build trigger ([8205c2e](https://github.com/meappy/kumon-marker/commit/8205c2e23adbbbaf52924b0709a6d52721c9544f))
* clear validation cache when refresh is clicked ([68154fc](https://github.com/meappy/kumon-marker/commit/68154fcdd8a21d48c58c3933c3c257cc289c3841))
* correct sheet_id matching logic in GDriveModal ([f469a03](https://github.com/meappy/kumon-marker/commit/f469a0322f4b6fc23f69127f348e4efe51ef8559))
* extract sheet_id from PDF text layer during refresh ([1931b4a](https://github.com/meappy/kumon-marker/commit/1931b4aa8d332c527bb4672ba15a34e264f6df11))
* force revalidation when refresh is clicked ([fc6bff6](https://github.com/meappy/kumon-marker/commit/fc6bff68c6604aa0c91aac2a7e120bcb56e0f50b))
* improve error handling for Google Drive API responses ([d383b1c](https://github.com/meappy/kumon-marker/commit/d383b1c57dc690b6049b533011002619cbe18480))
* improve error messages for Google Drive connection issues ([be13cfb](https://github.com/meappy/kumon-marker/commit/be13cfbf6e284bdf7d74e93ec1a8170c1b077f57))
* improve Google Drive file matching and add validation caching ([4c82288](https://github.com/meappy/kumon-marker/commit/4c82288873a10e05d36c00267819a0cf6b4756d2))
* improve OCR accuracy with image pre-processing ([117f09a](https://github.com/meappy/kumon-marker/commit/117f09aa37bb88e70015e25fd8415a37e26479a4))
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([2893278](https://github.com/meappy/kumon-marker/commit/28932780c71dd11f534965e88c9c2102ce594b1b))
* improve sheet ID and topic extraction from worksheets ([ff666cd](https://github.com/meappy/kumon-marker/commit/ff666cd00305c0aaafb54d78debb09c87338302a))
* log model name alongside vision provider in worker ([cda9a5e](https://github.com/meappy/kumon-marker/commit/cda9a5eaafb24576b3bc2b5f73ea030efc2a24e1))
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([435e4a8](https://github.com/meappy/kumon-marker/commit/435e4a89b3461c72808c3a6aa792b3bdec82f77f))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([95f8c06](https://github.com/meappy/kumon-marker/commit/95f8c06521e95bd4d60d7098e57e080b6fc28ef8))
* prevent HTTPException from being caught by generic exception handler ([e3bb523](https://github.com/meappy/kumon-marker/commit/e3bb5230859550a4dbcefcf01306ad1ea7d5d9a1))
* reduce memory requests to 512Mi for scheduling ([f8651aa](https://github.com/meappy/kumon-marker/commit/f8651aaf4658db25842cd9aea9d89784c7019d85))
* refresh now re-extracts sheet_ids instead of using cache ([cca27f5](https://github.com/meappy/kumon-marker/commit/cca27f5ffc2b740d60f308bf0d7c11684c13d59a))
* regex pattern now matches uppercase A/B suffix after .upper() ([2f529e3](https://github.com/meappy/kumon-marker/commit/2f529e3dff8bc4f3ec60995efa7e35272de7c76e))
* remove unused import ([699dbf1](https://github.com/meappy/kumon-marker/commit/699dbf1131d9ada7c55ef1956d8d1819c72431d9))
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([722a535](https://github.com/meappy/kumon-marker/commit/722a535cc04b87e3e3220e6d327f5728a247523a))
* run Google Drive scan in thread pool to prevent health check timeouts ([ba2de71](https://github.com/meappy/kumon-marker/commit/ba2de71c72328bfbfa54cf86922aa0424be1c0e5))
* separate refresh (fast) from revalidate (slow) for GDrive files ([7e22b40](https://github.com/meappy/kumon-marker/commit/7e22b404d2f8d2d32c36194b0b3ec53de21b06d3))
* session cookie secure flag and OAuth scope mismatch ([ba14bbd](https://github.com/meappy/kumon-marker/commit/ba14bbdcce62a5c9cf0cf2950c89c5bdbb00ceec))
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([46b4d37](https://github.com/meappy/kumon-marker/commit/46b4d37e40f8821afebaafe5e1054d8fb96880c3))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon ([ef27a79](https://github.com/meappy/kumon-marker/commit/ef27a794f54337a176a85959d4dfbae88a4bd0d8))
* store PKCE code_verifier in signed cookie for OAuth callback ([7d7084e](https://github.com/meappy/kumon-marker/commit/7d7084e2803c4db9fb692a47ce228f2639470ed4))
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([266c94c](https://github.com/meappy/kumon-marker/commit/266c94cccb2515ad3792cb2bab76b15d1c52dfc7))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([f48ca7f](https://github.com/meappy/kumon-marker/commit/f48ca7fd0a4ccfca342e2d1311bf34bd7e57c002))
* use filename for sheet_id extraction, simplify OCR ([e78d2d1](https://github.com/meappy/kumon-marker/commit/e78d2d1e3b87e78e845d3b020b011527e5626840))
* use vision model instead of unreliable Tesseract OCR for validation ([193df98](https://github.com/meappy/kumon-marker/commit/193df981c9e06a2f80f3aec53523a1c0bf391693))
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([7f14dfe](https://github.com/meappy/kumon-marker/commit/7f14dfe7ce0088f5d2d6138ca8cd450c83398636))


### Features

* add graceful shutdown for worker to complete in-progress jobs ([0f71362](https://github.com/meappy/kumon-marker/commit/0f713628675270b2136111ef4dd531590b31d53e))
* add group-by-student option for worksheet list ([62e9581](https://github.com/meappy/kumon-marker/commit/62e9581dcbd381da9c1f334bd4ebaabce803ba53))
* add ingress template and enable for production domain ([647fc61](https://github.com/meappy/kumon-marker/commit/647fc6188706fda5b7b522381f72281f84950a53))
* add pre-commit hook for branch protection and linting ([93a3dc0](https://github.com/meappy/kumon-marker/commit/93a3dc0c5fa94758129ee90f9723c5ec9276b5f5))
* add Revalidate button to GDrive modal ([6aa4f4a](https://github.com/meappy/kumon-marker/commit/6aa4f4a21e46843c3de90acf251f6c5d39dbaad3))
* add user to allowed users list ([04b264e](https://github.com/meappy/kumon-marker/commit/04b264e5fc178d4e9ad0eddd7e9d107a1f7d1b55))
* dual secret support and ArgoCD multi-source secrets repo ([1610065](https://github.com/meappy/kumon-marker/commit/1610065fed9d3da706883e2ddc60d471b6843d0b))
* move allowed users to private secrets repo ([d7ef576](https://github.com/meappy/kumon-marker/commit/d7ef576edd3edd3eed891b0945d0772133524fa5))
* move ingress host and internal IPs to private secrets repo ([c6fd45d](https://github.com/meappy/kumon-marker/commit/c6fd45da12263bb46a996d9fdfeda88236ce29a2))
* refactor to pluggable multi-provider architecture ([31c5c2c](https://github.com/meappy/kumon-marker/commit/31c5c2cee1c636e15912bcb96316ee4a6c637589))
* switch from Claude CLI to API mode ([fed6fab](https://github.com/meappy/kumon-marker/commit/fed6fab01e765844a0bdb62eaf913458007e8ae3))
* use claude-opus-4-6 model for worksheet analysis ([e9dd98c](https://github.com/meappy/kumon-marker/commit/e9dd98c243b8d0a85b48e14f8c47737c10d9eec0))
* use Tesseract OCR for sheet ID extraction ([1b9c413](https://github.com/meappy/kumon-marker/commit/1b9c413b618b7138ee0f07179fcf4d3d03f34509))


### Performance Improvements

* extract sheet_id from filename first, skip download if valid ([6a801e6](https://github.com/meappy/kumon-marker/commit/6a801e651c8d4495da8b2db5e53c19a162fa164a))

## [0.6.2](https://github.com/meappy/kumon-marker/compare/v0.6.1...v0.6.2) (2026-01-25)


### Bug Fixes

* improve Google Drive file matching and add validation caching ([9ea2a50](https://github.com/meappy/kumon-marker/commit/9ea2a5040edb66ff46dcac9c4b6807c0c86a7d6f))

## [0.6.1](https://github.com/meappy/kumon-marker/compare/v0.6.0...v0.6.1) (2026-01-25)


### Bug Fixes

* session cookie secure flag and OAuth scope mismatch ([91011cd](https://github.com/meappy/kumon-marker/commit/91011cdf2545f301cbcff4258a444747e393dd8b))

# [0.6.0](https://github.com/meappy/kumon-marker/compare/v0.5.3...v0.6.0) (2026-01-19)


### Features

* add REDACTED to allowed users ([f102680](https://github.com/meappy/kumon-marker/commit/f102680dd93da8b54f68003d197d6f0cbe7364ce))

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
