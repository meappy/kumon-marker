## [1.10.4](https://github.com/meappy/kumon-marker/compare/v1.10.3...v1.10.4) (2026-03-20)


### Bug Fixes

* GDrive modal shows tick immediately instead of job progress ([#62](https://github.com/meappy/kumon-marker/issues/62)) ([ac2cc04](https://github.com/meappy/kumon-marker/commit/ac2cc04188c2c034db46b074ce018a884707ed0b))

## [1.10.3](https://github.com/meappy/kumon-marker/compare/v1.10.2...v1.10.3) (2026-03-20)


### Bug Fixes

* restore to_dict() on Job model (was accidentally moved to Share) ([#61](https://github.com/meappy/kumon-marker/issues/61)) ([d67ba97](https://github.com/meappy/kumon-marker/commit/d67ba971d5def9422f67806b073db7a038c1efa4))

## [1.10.2](https://github.com/meappy/kumon-marker/compare/v1.10.1...v1.10.2) (2026-03-20)


### Bug Fixes

* switch from claude-opus-4-6 to claude-haiku-4-5 for OAuth token compatibility ([#60](https://github.com/meappy/kumon-marker/issues/60)) ([0b2da7f](https://github.com/meappy/kumon-marker/commit/0b2da7f4d8d4e80b638b88c5e2878076af2bce84))

## [1.10.1](https://github.com/meappy/kumon-marker/compare/v1.10.0...v1.10.1) (2026-03-19)


### Bug Fixes

* set openebs-rwx storage class in argocd values ([#59](https://github.com/meappy/kumon-marker/issues/59)) ([1af616f](https://github.com/meappy/kumon-marker/commit/1af616fd8b018d6a1bbc5d692ee0d32f54ef0337))

# [1.10.0](https://github.com/meappy/kumon-marker/compare/v1.9.1...v1.10.0) (2026-03-18)


### Features

* switch data and RabbitMQ PVCs to RWX storage (openebs-rwx) ([#58](https://github.com/meappy/kumon-marker/issues/58)) ([35b5aae](https://github.com/meappy/kumon-marker/commit/35b5aae84c3ccd00aa5e34962aca6745834f78bd))

## [1.9.1](https://github.com/meappy/kumon-marker/compare/v1.9.0...v1.9.1) (2026-03-17)


### Bug Fixes

* RabbitMQ Recreate strategy for RWO volume ([#57](https://github.com/meappy/kumon-marker/issues/57)) ([7beb7ba](https://github.com/meappy/kumon-marker/commit/7beb7ba01eb1e6e3eb49b21e7e3122114c36da65))

# [1.9.0](https://github.com/meappy/kumon-marker/compare/v1.8.0...v1.9.0) (2026-03-16)


### Features

* wire DB pool env vars through Helm values ([#56](https://github.com/meappy/kumon-marker/issues/56)) ([ca37015](https://github.com/meappy/kumon-marker/commit/ca37015fc0168755f12cea05f63be53697d090f3))

# [1.8.0](https://github.com/meappy/kumon-marker/compare/v1.7.10...v1.8.0) (2026-03-16)


### Features

* make DB pool settings configurable via env vars ([#55](https://github.com/meappy/kumon-marker/issues/55)) ([326883c](https://github.com/meappy/kumon-marker/commit/326883cc33c6b32a8754c829a71bff6d210bddf0))

## [1.7.10](https://github.com/meappy/kumon-marker/compare/v1.7.9...v1.7.10) (2026-03-16)


### Bug Fixes

* add sslmode=require for DO PgBouncer ([#54](https://github.com/meappy/kumon-marker/issues/54)) ([759ba63](https://github.com/meappy/kumon-marker/commit/759ba63c00b30aff3a3c44bbb094eed682022696))

## [1.7.9](https://github.com/meappy/kumon-marker/compare/v1.7.8...v1.7.9) (2026-03-16)


### Bug Fixes

* disable native hstore for PgBouncer compatibility ([#53](https://github.com/meappy/kumon-marker/issues/53)) ([1db21ef](https://github.com/meappy/kumon-marker/commit/1db21ef4a38ed403915a62e87c4882c683763fea))

## [1.7.8](https://github.com/meappy/kumon-marker/compare/v1.7.7...v1.7.8) (2026-03-16)


### Bug Fixes

* move database port to secrets repo ([#52](https://github.com/meappy/kumon-marker/issues/52)) ([98e9a92](https://github.com/meappy/kumon-marker/commit/98e9a921358edd6fc45635d9f2793def9f7ab9a0))

## [1.7.7](https://github.com/meappy/kumon-marker/compare/v1.7.6...v1.7.7) (2026-03-16)


### Bug Fixes

* DB connection pooling and worker external DB support ([#51](https://github.com/meappy/kumon-marker/issues/51)) ([9f79972](https://github.com/meappy/kumon-marker/commit/9f7997257586cf513fae3dbb7176d9f98fb9717c))

## [1.7.6](https://github.com/meappy/kumon-marker/compare/v1.7.5...v1.7.6) (2026-03-16)


### Bug Fixes

* reduce RabbitMQ and default resource limits ([#50](https://github.com/meappy/kumon-marker/issues/50)) ([85484d2](https://github.com/meappy/kumon-marker/commit/85484d2d940ab7e8865b0562671e65c0ce23e0b3))

## [1.7.5](https://github.com/meappy/kumon-marker/compare/v1.7.4...v1.7.5) (2026-03-16)


### Bug Fixes

* reduce memory limits to 256Mi ([#49](https://github.com/meappy/kumon-marker/issues/49)) ([d88a1fc](https://github.com/meappy/kumon-marker/commit/d88a1fca46c3b66dba7dfceafe32f365772b108c))

## [1.7.4](https://github.com/meappy/kumon-marker/compare/v1.7.3...v1.7.4) (2026-03-16)


### Bug Fixes

* reduce memory limits for DO cluster ([#48](https://github.com/meappy/kumon-marker/issues/48)) ([c875c0a](https://github.com/meappy/kumon-marker/commit/c875c0a7f58b6c8efea293a4d67b4857d8ee0bb8))

## [1.7.3](https://github.com/meappy/kumon-marker/compare/v1.7.2...v1.7.3) (2026-03-16)


### Bug Fixes

* add email-validator dependency to resolve pydantic import error ([#47](https://github.com/meappy/kumon-marker/issues/47)) ([a226c46](https://github.com/meappy/kumon-marker/commit/a226c46035f623d45bcf3750ee5e27ffbc8b9150))

## [1.7.2](https://github.com/meappy/kumon-marker/compare/v1.7.1...v1.7.2) (2026-03-16)


### Bug Fixes

* disable in-cluster PG, use ClusterIP service for DO ([#46](https://github.com/meappy/kumon-marker/issues/46)) ([b4682e5](https://github.com/meappy/kumon-marker/commit/b4682e5078dcaf46aac0134c0d41b4052532d875))

## [1.7.1](https://github.com/meappy/kumon-marker/compare/v1.7.0...v1.7.1) (2026-03-16)


### Bug Fixes

* rename database from kumon to kumon-marker ([#45](https://github.com/meappy/kumon-marker/issues/45)) ([177a501](https://github.com/meappy/kumon-marker/commit/177a5019a1315d33e7973e07c95ad940f1cb1dd7))

# [1.7.0](https://github.com/meappy/kumon-marker/compare/v1.6.0...v1.7.0) (2026-03-16)


### Features

* switch to DO Managed PostgreSQL ([#44](https://github.com/meappy/kumon-marker/issues/44)) ([578ad54](https://github.com/meappy/kumon-marker/commit/578ad540621edce5dae0b318433dbe280a1e023a))

# [1.6.0](https://github.com/meappy/kumon-marker/compare/v1.5.4...v1.6.0) (2026-03-16)


### Features

* add dashboard sharing with read/readwrite permissions ([#43](https://github.com/meappy/kumon-marker/issues/43)) ([4486d5f](https://github.com/meappy/kumon-marker/commit/4486d5f1f8bc5f322005e98955c3407d6c1eaff5))

## [1.5.4](https://github.com/meappy/kumon-marker/compare/v1.5.3...v1.5.4) (2026-03-15)


### Bug Fixes

* only use LLM fallback for truly image-only PDFs with no text layer ([#42](https://github.com/meappy/kumon-marker/issues/42)) ([b5f96ed](https://github.com/meappy/kumon-marker/commit/b5f96ed02666b34cb95d629180a7e816f2840681))

## [1.5.3](https://github.com/meappy/kumon-marker/compare/v1.5.2...v1.5.3) (2026-03-15)


### Bug Fixes

* use broader regex KUM.N for OCR misreadings of KUMON in GDrive scan ([#41](https://github.com/meappy/kumon-marker/issues/41)) ([51e6249](https://github.com/meappy/kumon-marker/commit/51e624940bb69209bed57377f659922f842e56f2))

## [1.5.2](https://github.com/meappy/kumon-marker/compare/v1.5.1...v1.5.2) (2026-03-15)


### Bug Fixes

* handle OCR misreading of KUMON (e.g. KUMQN) in GDrive scan ([#40](https://github.com/meappy/kumon-marker/issues/40)) ([9f017c0](https://github.com/meappy/kumon-marker/commit/9f017c0609c8b001ced8d225f72c338a9bee8c41))

## [1.5.1](https://github.com/meappy/kumon-marker/compare/v1.5.0...v1.5.1) (2026-03-15)


### Bug Fixes

* use LLM vision fallback when GDrive scan text layer check fails ([#39](https://github.com/meappy/kumon-marker/issues/39)) ([35071d4](https://github.com/meappy/kumon-marker/commit/35071d457a619aabb881cb4d34c9b28aecdb1cf6))

# [1.5.0](https://github.com/meappy/kumon-marker/compare/v1.4.1...v1.5.0) (2026-03-13)


### Features

* add PDF preview for Google Drive files ([#38](https://github.com/meappy/kumon-marker/issues/38)) ([2849d7d](https://github.com/meappy/kumon-marker/commit/2849d7daae79331fb88bd7f8e18974001028e41c))

## [1.4.1](https://github.com/meappy/kumon-marker/compare/v1.4.0...v1.4.1) (2026-03-09)


### Bug Fixes

* widen desktop layout from max-w-2xl to max-w-4xl and prevent Delete All text wrapping ([#37](https://github.com/meappy/kumon-marker/issues/37)) ([b5a2bf7](https://github.com/meappy/kumon-marker/commit/b5a2bf76d21921eb1f659df6b4bd693fe3204c64))

# [1.4.0](https://github.com/meappy/kumon-marker/compare/v1.3.0...v1.4.0) (2026-03-09)


### Bug Fixes

* show meaningful names in marking queue ([#34](https://github.com/meappy/kumon-marker/issues/34)) ([9543d0e](https://github.com/meappy/kumon-marker/commit/9543d0eab126bdc7f245ad68b1f6a17712e48411))
* update GDrive cache with corrected sheet ID after processing ([#36](https://github.com/meappy/kumon-marker/issues/36)) ([1857bfd](https://github.com/meappy/kumon-marker/commit/1857bfde36cd7cfeceb5981f96bfcf93266d7c84))


### Features

* clean up header with kebab menu and fixed-width layout ([#35](https://github.com/meappy/kumon-marker/issues/35)) ([7a7c981](https://github.com/meappy/kumon-marker/commit/7a7c9817a0f1ad881afef4f8af3e0919001f7248))

# [1.3.0](https://github.com/meappy/kumon-marker/compare/v1.2.0...v1.3.0) (2026-03-09)


### Features

* persist sort/group preferences and add re-mark button ([#33](https://github.com/meappy/kumon-marker/issues/33)) ([981baf7](https://github.com/meappy/kumon-marker/commit/981baf7545c05c45b9c4aed65929c20ce368a041))

# [1.2.0](https://github.com/meappy/kumon-marker/compare/v1.1.2...v1.2.0) (2026-03-09)


### Features

* add English worksheet marking support ([#32](https://github.com/meappy/kumon-marker/issues/32)) ([09fbab6](https://github.com/meappy/kumon-marker/commit/09fbab6f23f97fd60eddfbc6f664be80da0ccc35))

## [1.1.2](https://github.com/meappy/kumon-marker/compare/v1.1.1...v1.1.2) (2026-03-09)


### Bug Fixes

* always use vision model for sheet ID when validation is llm ([#31](https://github.com/meappy/kumon-marker/issues/31)) ([037b2ef](https://github.com/meappy/kumon-marker/commit/037b2ef03c8d6550ec1ccb7c8814e2ea3bcaf381))

## [1.1.1](https://github.com/meappy/kumon-marker/compare/v1.1.0...v1.1.1) (2026-03-09)


### Bug Fixes

* improve vision model sheet ID extraction accuracy ([#30](https://github.com/meappy/kumon-marker/issues/30)) ([a891d13](https://github.com/meappy/kumon-marker/commit/a891d1301e7b995ec1d2d4de9cb03ead3b49a959))

# [1.1.0](https://github.com/meappy/kumon-marker/compare/v1.0.3...v1.1.0) (2026-03-09)


### Features

* run Google Drive scan in background so it continues when modal is closed ([#29](https://github.com/meappy/kumon-marker/issues/29)) ([c8e34cc](https://github.com/meappy/kumon-marker/commit/c8e34ccb23ab830a20b6531ba44feae2c13c852f))

## [1.0.3](https://github.com/meappy/kumon-marker/compare/v1.0.2...v1.0.3) (2026-03-09)


### Bug Fixes

* regenerate favicon from logo.svg to match header branding ([#28](https://github.com/meappy/kumon-marker/issues/28)) ([5e64fac](https://github.com/meappy/kumon-marker/commit/5e64fac478b782aec54279bd3c84e68795c33fe3))

## [1.0.2](https://github.com/meappy/kumon-marker/compare/v1.0.1...v1.0.2) (2026-03-09)


### Bug Fixes

* use latest Docker image tag for correct branding ([#27](https://github.com/meappy/kumon-marker/issues/27)) ([c825c11](https://github.com/meappy/kumon-marker/commit/c825c11393afe85efdcbb5847ac6b98917e5ce18))

## [1.0.1](https://github.com/meappy/kumon-marker/compare/v1.0.0...v1.0.1) (2026-03-08)


### Bug Fixes

* update image tag to 1.0.4 with correct branding ([#26](https://github.com/meappy/kumon-marker/issues/26)) ([585cf77](https://github.com/meappy/kumon-marker/commit/585cf779df05d10066cbb68c7a4fdba53547b57c))

# 1.0.0 (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([47817db](https://github.com/meappy/kumon-marker/commit/47817db79277346b27db8f77d63ec31edded9db7))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([4eb817f](https://github.com/meappy/kumon-marker/commit/4eb817fa5b1ecfad85779a4cfe22244a7b6f1b89))
* add quick text-layer check to filter non-Kumon PDFs ([b88e4f6](https://github.com/meappy/kumon-marker/commit/b88e4f687ec78fb172f1050687014cca755caf16))
* add values-local.yaml.example template and security improvements ([8f3b9e5](https://github.com/meappy/kumon-marker/commit/8f3b9e5e5c47dd08e4ce16d81be83a2d5b9e9b8a))
* build multi-platform Docker images (amd64 + arm64) ([c0ccbab](https://github.com/meappy/kumon-marker/commit/c0ccbab24e605c3e6299c71f40fd51d13ee3bb6b))
* capture semantic-release output for Docker build trigger ([8205c2e](https://github.com/meappy/kumon-marker/commit/8205c2e23adbbbaf52924b0709a6d52721c9544f))
* clear validation cache when refresh is clicked ([ad302f1](https://github.com/meappy/kumon-marker/commit/ad302f1bbbc861ac6dc1d784dc71c2715486eefc))
* correct sheet_id matching logic in GDriveModal ([6d407c1](https://github.com/meappy/kumon-marker/commit/6d407c18de10c63bb4cb118d5a4cd4c08465c75f))
* extract sheet_id from PDF text layer during refresh ([294e279](https://github.com/meappy/kumon-marker/commit/294e279b0181bbc9f9d60f6701022872ecffd961))
* force revalidation when refresh is clicked ([19f4c40](https://github.com/meappy/kumon-marker/commit/19f4c4075d34da6529e036b2e5c57386b00fc587))
* improve error handling for Google Drive API responses ([9e112b9](https://github.com/meappy/kumon-marker/commit/9e112b9eedeb0a5ddde9b152f9e4fe27ed8eb5e9))
* improve error messages for Google Drive connection issues ([20ed824](https://github.com/meappy/kumon-marker/commit/20ed824ef65d104ee0023b47e6df81a63dbded1e))
* improve Google Drive file matching and add validation caching ([ab6e86d](https://github.com/meappy/kumon-marker/commit/ab6e86df462dc0afd024c68379379989fbb0949a))
* improve OCR accuracy with image pre-processing ([d84c0a6](https://github.com/meappy/kumon-marker/commit/d84c0a6acbfb2554118c4b1ed829de0964f3f406))
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([2893278](https://github.com/meappy/kumon-marker/commit/28932780c71dd11f534965e88c9c2102ce594b1b))
* improve sheet ID and topic extraction from worksheets ([990bed3](https://github.com/meappy/kumon-marker/commit/990bed3a9c3cf93d76d23ce827d37c1fb522ee1a))
* log model name alongside vision provider in worker ([8e4e74d](https://github.com/meappy/kumon-marker/commit/8e4e74d5d2d13d1a3b6e9d84e81339a76e13d7dc))
* make applicationset.yaml a generic template ([0c9cb1d](https://github.com/meappy/kumon-marker/commit/0c9cb1d01b48c7eb36e671de4b6d70672a267e89))
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([d24e59a](https://github.com/meappy/kumon-marker/commit/d24e59a62b1533f1bda94a7d4f1e747245fb4359))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([8204a0e](https://github.com/meappy/kumon-marker/commit/8204a0ec5de99a00589f20a21beb4428b1937fdc))
* prevent HTTPException from being caught by generic exception handler ([f780563](https://github.com/meappy/kumon-marker/commit/f780563098c7bf79750607673edafa31543039cf))
* reduce memory requests to 512Mi for scheduling ([6e36cdc](https://github.com/meappy/kumon-marker/commit/6e36cdc6a7a6d46a4f9c4a005241457cef014222))
* refresh now re-extracts sheet_ids instead of using cache ([a4b5512](https://github.com/meappy/kumon-marker/commit/a4b5512a452db4ecd5cdb0163e0f0a0db50a26ff))
* regex pattern now matches uppercase A/B suffix after .upper() ([154eece](https://github.com/meappy/kumon-marker/commit/154eece0e3fc7c9b766adb19cac10619e6bada94))
* remove personal email from changelog entry ([#23](https://github.com/meappy/kumon-marker/issues/23)) ([bf44f25](https://github.com/meappy/kumon-marker/commit/bf44f2579ac07d9143b9702089b0c864a022ffa8))
* remove unused import ([15373dd](https://github.com/meappy/kumon-marker/commit/15373dd17a98038f9bd15269686238fe2bf8fe1d))
* replace banner with dark navy background for dark mode ([f03c10d](https://github.com/meappy/kumon-marker/commit/f03c10db3c693c4a696a95d3973a256c1750091e))
* replace emoji placeholders with actual logo branding ([#20](https://github.com/meappy/kumon-marker/issues/20)) ([f32b57a](https://github.com/meappy/kumon-marker/commit/f32b57a3416028a2c806326c80a5c0895cd78f23))
* resolve lint errors in backend and frontend ([abddb84](https://github.com/meappy/kumon-marker/commit/abddb84a0872b272d53753b92ae7163c00f0020b))
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([641bba6](https://github.com/meappy/kumon-marker/commit/641bba603ce4ba959e911ac503c84b1a340f3025))
* restore README badges lost during history rewrite ([8e937f8](https://github.com/meappy/kumon-marker/commit/8e937f837a812e32c5b8c4843cabbe1f3e804400))
* run Google Drive scan in thread pool to prevent health check timeouts ([9f22d84](https://github.com/meappy/kumon-marker/commit/9f22d84bdf22060140f7202f96ebeafc9ad2e5e7))
* separate refresh (fast) from revalidate (slow) for GDrive files ([1e470b9](https://github.com/meappy/kumon-marker/commit/1e470b9f451bc355746fa744abec9bfb3edddac2))
* session cookie secure flag and OAuth scope mismatch ([530887b](https://github.com/meappy/kumon-marker/commit/530887b05d1e5779a4421c8d948488adb0ba3b76))
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([c0ce47b](https://github.com/meappy/kumon-marker/commit/c0ce47bc5c7ab88cd178201ec1284293056f2168))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon ([d507491](https://github.com/meappy/kumon-marker/commit/d507491d3dfbb04fb1d5ae139a890126a20e7ff4))
* store PKCE code_verifier in signed cookie for OAuth callback ([452e8b2](https://github.com/meappy/kumon-marker/commit/452e8b245440af348465bbf1370cd5a893031198))
* strip dead commit links from changelog after history rewrite ([6ec735b](https://github.com/meappy/kumon-marker/commit/6ec735b7c8fd86087b85ea088088bbbe56b9923d))
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([021b1fb](https://github.com/meappy/kumon-marker/commit/021b1fbad73f55d13ec87e534a8e9b1cb7f47c19))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([7354aa4](https://github.com/meappy/kumon-marker/commit/7354aa4ea712303b89d3a036a64f7d20f90133d0))
* unify branding with consistent SVG logo across all assets ([#21](https://github.com/meappy/kumon-marker/issues/21)) ([c17709d](https://github.com/meappy/kumon-marker/commit/c17709d153a53d1931a3de14d8ffea0fa8b83cc3))
* update branding with white outlines for dark mode support ([509a4f4](https://github.com/meappy/kumon-marker/commit/509a4f4df3c718c80f5fcd7300cd5455bfa704b6))
* update release workflow permissions for ghcr.io ([079dbf5](https://github.com/meappy/kumon-marker/commit/079dbf5da9be6564368a31c89601b6523ddf41e0))
* use filename for sheet_id extraction, simplify OCR ([51294d7](https://github.com/meappy/kumon-marker/commit/51294d7e29efcfd28b56f4e699dcd5e0db052ed0))
* use vision model instead of unreliable Tesseract OCR for validation ([3ad7484](https://github.com/meappy/kumon-marker/commit/3ad7484c82f80d756a3649b0083f00a24b9c9dbb))
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([087052f](https://github.com/meappy/kumon-marker/commit/087052f3b89de9ad9b3a1df1c45342e81e2b23b2))


### Features

* add branding assets and update README ([5fa9ed0](https://github.com/meappy/kumon-marker/commit/5fa9ed01d867b4127243a5f7aa090859c0f3f51a))
* add GitOps CI/CD with Semantic Release and Argo CD ([3920d2b](https://github.com/meappy/kumon-marker/commit/3920d2b18dce4aab1365e26fe89859d252c1ec61))
* add graceful shutdown for worker to complete in-progress jobs ([8c76fdb](https://github.com/meappy/kumon-marker/commit/8c76fdbf97c8d4f6b2e11bf5df1b8225c1aa3116))
* add group-by-student option for worksheet list ([525ae79](https://github.com/meappy/kumon-marker/commit/525ae79a0031d51692e03fd025d387f939c4937e))
* add ingress template and enable for production domain ([f8c3229](https://github.com/meappy/kumon-marker/commit/f8c32298ed92b91f22fe467b2f884b5d304fec09))
* add MIT license and fix banner for dark mode ([012169e](https://github.com/meappy/kumon-marker/commit/012169ed9fd0861eef99c304e95247043d036498))
* add pre-commit hook for branch protection and linting ([75ec0db](https://github.com/meappy/kumon-marker/commit/75ec0dbf2ec547e4679e4cdb97c3338ab2ecbed7))
* add Revalidate button to GDrive modal ([40ea8f0](https://github.com/meappy/kumon-marker/commit/40ea8f00c9f6e485862b180500966c290e7d91a7))
* add user to allowed users list ([ef46895](https://github.com/meappy/kumon-marker/commit/ef468959d9fb96a18ea0122ddc41a9114469b1ac))
* auto-deploy branches via Argo CD ([3269e44](https://github.com/meappy/kumon-marker/commit/3269e44aca665f1d9ddd99d86fb164cdf1db60d9))
* dual secret support and ArgoCD multi-source secrets repo ([1aad047](https://github.com/meappy/kumon-marker/commit/1aad04738cb25c6fea5fa1039122cfd58233dd2d))
* initial commit with full application ([dc7dff2](https://github.com/meappy/kumon-marker/commit/dc7dff28ecd14a07dce7a97041fed2db18fb6766))
* move allowed users to private secrets repo ([48de9e3](https://github.com/meappy/kumon-marker/commit/48de9e3ef20aaf6c453f467d191c8efb14dc24be))
* move ArgoCD webhook URL to GitHub secrets ([0c154ed](https://github.com/meappy/kumon-marker/commit/0c154ed20e01892dbba2030800060d1b9339bba8))
* move ingress host and internal IPs to private secrets repo ([f3f43d4](https://github.com/meappy/kumon-marker/commit/f3f43d43d45ff4fb78f4bd7f73c7ed4f2c48c5bf))
* refactor to pluggable multi-provider architecture ([e2544b9](https://github.com/meappy/kumon-marker/commit/e2544b96f97b64aeae2f9f05f521f008996ee8b4))
* switch from Claude CLI to API mode ([93f1857](https://github.com/meappy/kumon-marker/commit/93f1857cf39c3264d152377294451684cecd915d))
* use claude-opus-4-6 model for worksheet analysis ([6bc171e](https://github.com/meappy/kumon-marker/commit/6bc171e0817e519418d0314130172313867c511d))
* use Tesseract OCR for sheet ID extraction ([e980490](https://github.com/meappy/kumon-marker/commit/e980490d4c39e8f6187502043b3e1d79e706df74))


### Performance Improvements

* extract sheet_id from filename first, skip download if valid ([d6ed871](https://github.com/meappy/kumon-marker/commit/d6ed8712f1d5dfdb8d82fa0f7a81622e41d939f8))

# 1.0.0 (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([47817db](https://github.com/meappy/kumon-marker/commit/47817db79277346b27db8f77d63ec31edded9db7))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([4eb817f](https://github.com/meappy/kumon-marker/commit/4eb817fa5b1ecfad85779a4cfe22244a7b6f1b89))
* add quick text-layer check to filter non-Kumon PDFs ([b88e4f6](https://github.com/meappy/kumon-marker/commit/b88e4f687ec78fb172f1050687014cca755caf16))
* add values-local.yaml.example template and security improvements ([8f3b9e5](https://github.com/meappy/kumon-marker/commit/8f3b9e5e5c47dd08e4ce16d81be83a2d5b9e9b8a))
* build multi-platform Docker images (amd64 + arm64) ([c0ccbab](https://github.com/meappy/kumon-marker/commit/c0ccbab24e605c3e6299c71f40fd51d13ee3bb6b))
* capture semantic-release output for Docker build trigger ([8205c2e](https://github.com/meappy/kumon-marker/commit/8205c2e23adbbbaf52924b0709a6d52721c9544f))
* clear validation cache when refresh is clicked ([ad302f1](https://github.com/meappy/kumon-marker/commit/ad302f1bbbc861ac6dc1d784dc71c2715486eefc))
* correct sheet_id matching logic in GDriveModal ([6d407c1](https://github.com/meappy/kumon-marker/commit/6d407c18de10c63bb4cb118d5a4cd4c08465c75f))
* extract sheet_id from PDF text layer during refresh ([294e279](https://github.com/meappy/kumon-marker/commit/294e279b0181bbc9f9d60f6701022872ecffd961))
* force revalidation when refresh is clicked ([19f4c40](https://github.com/meappy/kumon-marker/commit/19f4c4075d34da6529e036b2e5c57386b00fc587))
* improve error handling for Google Drive API responses ([9e112b9](https://github.com/meappy/kumon-marker/commit/9e112b9eedeb0a5ddde9b152f9e4fe27ed8eb5e9))
* improve error messages for Google Drive connection issues ([20ed824](https://github.com/meappy/kumon-marker/commit/20ed824ef65d104ee0023b47e6df81a63dbded1e))
* improve Google Drive file matching and add validation caching ([ab6e86d](https://github.com/meappy/kumon-marker/commit/ab6e86df462dc0afd024c68379379989fbb0949a))
* improve OCR accuracy with image pre-processing ([d84c0a6](https://github.com/meappy/kumon-marker/commit/d84c0a6acbfb2554118c4b1ed829de0964f3f406))
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([2893278](https://github.com/meappy/kumon-marker/commit/28932780c71dd11f534965e88c9c2102ce594b1b))
* improve sheet ID and topic extraction from worksheets ([990bed3](https://github.com/meappy/kumon-marker/commit/990bed3a9c3cf93d76d23ce827d37c1fb522ee1a))
* log model name alongside vision provider in worker ([8e4e74d](https://github.com/meappy/kumon-marker/commit/8e4e74d5d2d13d1a3b6e9d84e81339a76e13d7dc))
* make applicationset.yaml a generic template ([0c9cb1d](https://github.com/meappy/kumon-marker/commit/0c9cb1d01b48c7eb36e671de4b6d70672a267e89))
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([d24e59a](https://github.com/meappy/kumon-marker/commit/d24e59a62b1533f1bda94a7d4f1e747245fb4359))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([8204a0e](https://github.com/meappy/kumon-marker/commit/8204a0ec5de99a00589f20a21beb4428b1937fdc))
* prevent HTTPException from being caught by generic exception handler ([f780563](https://github.com/meappy/kumon-marker/commit/f780563098c7bf79750607673edafa31543039cf))
* reduce memory requests to 512Mi for scheduling ([6e36cdc](https://github.com/meappy/kumon-marker/commit/6e36cdc6a7a6d46a4f9c4a005241457cef014222))
* refresh now re-extracts sheet_ids instead of using cache ([a4b5512](https://github.com/meappy/kumon-marker/commit/a4b5512a452db4ecd5cdb0163e0f0a0db50a26ff))
* regex pattern now matches uppercase A/B suffix after .upper() ([154eece](https://github.com/meappy/kumon-marker/commit/154eece0e3fc7c9b766adb19cac10619e6bada94))
* remove personal email from changelog entry ([#23](https://github.com/meappy/kumon-marker/issues/23)) ([bf44f25](https://github.com/meappy/kumon-marker/commit/bf44f2579ac07d9143b9702089b0c864a022ffa8))
* remove unused import ([15373dd](https://github.com/meappy/kumon-marker/commit/15373dd17a98038f9bd15269686238fe2bf8fe1d))
* replace banner with dark navy background for dark mode ([f03c10d](https://github.com/meappy/kumon-marker/commit/f03c10db3c693c4a696a95d3973a256c1750091e))
* replace emoji placeholders with actual logo branding ([#20](https://github.com/meappy/kumon-marker/issues/20)) ([f32b57a](https://github.com/meappy/kumon-marker/commit/f32b57a3416028a2c806326c80a5c0895cd78f23))
* resolve lint errors in backend and frontend ([abddb84](https://github.com/meappy/kumon-marker/commit/abddb84a0872b272d53753b92ae7163c00f0020b))
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([641bba6](https://github.com/meappy/kumon-marker/commit/641bba603ce4ba959e911ac503c84b1a340f3025))
* run Google Drive scan in thread pool to prevent health check timeouts ([9f22d84](https://github.com/meappy/kumon-marker/commit/9f22d84bdf22060140f7202f96ebeafc9ad2e5e7))
* separate refresh (fast) from revalidate (slow) for GDrive files ([1e470b9](https://github.com/meappy/kumon-marker/commit/1e470b9f451bc355746fa744abec9bfb3edddac2))
* session cookie secure flag and OAuth scope mismatch ([530887b](https://github.com/meappy/kumon-marker/commit/530887b05d1e5779a4421c8d948488adb0ba3b76))
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([c0ce47b](https://github.com/meappy/kumon-marker/commit/c0ce47bc5c7ab88cd178201ec1284293056f2168))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon ([d507491](https://github.com/meappy/kumon-marker/commit/d507491d3dfbb04fb1d5ae139a890126a20e7ff4))
* store PKCE code_verifier in signed cookie for OAuth callback ([452e8b2](https://github.com/meappy/kumon-marker/commit/452e8b245440af348465bbf1370cd5a893031198))
* strip dead commit links from changelog after history rewrite ([6ec735b](https://github.com/meappy/kumon-marker/commit/6ec735b7c8fd86087b85ea088088bbbe56b9923d))
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([021b1fb](https://github.com/meappy/kumon-marker/commit/021b1fbad73f55d13ec87e534a8e9b1cb7f47c19))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([7354aa4](https://github.com/meappy/kumon-marker/commit/7354aa4ea712303b89d3a036a64f7d20f90133d0))
* unify branding with consistent SVG logo across all assets ([#21](https://github.com/meappy/kumon-marker/issues/21)) ([c17709d](https://github.com/meappy/kumon-marker/commit/c17709d153a53d1931a3de14d8ffea0fa8b83cc3))
* update branding with white outlines for dark mode support ([509a4f4](https://github.com/meappy/kumon-marker/commit/509a4f4df3c718c80f5fcd7300cd5455bfa704b6))
* update release workflow permissions for ghcr.io ([079dbf5](https://github.com/meappy/kumon-marker/commit/079dbf5da9be6564368a31c89601b6523ddf41e0))
* use filename for sheet_id extraction, simplify OCR ([51294d7](https://github.com/meappy/kumon-marker/commit/51294d7e29efcfd28b56f4e699dcd5e0db052ed0))
* use vision model instead of unreliable Tesseract OCR for validation ([3ad7484](https://github.com/meappy/kumon-marker/commit/3ad7484c82f80d756a3649b0083f00a24b9c9dbb))
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([087052f](https://github.com/meappy/kumon-marker/commit/087052f3b89de9ad9b3a1df1c45342e81e2b23b2))


### Features

* add branding assets and update README ([5fa9ed0](https://github.com/meappy/kumon-marker/commit/5fa9ed01d867b4127243a5f7aa090859c0f3f51a))
* add GitOps CI/CD with Semantic Release and Argo CD ([3920d2b](https://github.com/meappy/kumon-marker/commit/3920d2b18dce4aab1365e26fe89859d252c1ec61))
* add graceful shutdown for worker to complete in-progress jobs ([8c76fdb](https://github.com/meappy/kumon-marker/commit/8c76fdbf97c8d4f6b2e11bf5df1b8225c1aa3116))
* add group-by-student option for worksheet list ([525ae79](https://github.com/meappy/kumon-marker/commit/525ae79a0031d51692e03fd025d387f939c4937e))
* add ingress template and enable for production domain ([f8c3229](https://github.com/meappy/kumon-marker/commit/f8c32298ed92b91f22fe467b2f884b5d304fec09))
* add MIT license and fix banner for dark mode ([012169e](https://github.com/meappy/kumon-marker/commit/012169ed9fd0861eef99c304e95247043d036498))
* add pre-commit hook for branch protection and linting ([75ec0db](https://github.com/meappy/kumon-marker/commit/75ec0dbf2ec547e4679e4cdb97c3338ab2ecbed7))
* add Revalidate button to GDrive modal ([40ea8f0](https://github.com/meappy/kumon-marker/commit/40ea8f00c9f6e485862b180500966c290e7d91a7))
* add user to allowed users list ([ef46895](https://github.com/meappy/kumon-marker/commit/ef468959d9fb96a18ea0122ddc41a9114469b1ac))
* auto-deploy branches via Argo CD ([3269e44](https://github.com/meappy/kumon-marker/commit/3269e44aca665f1d9ddd99d86fb164cdf1db60d9))
* dual secret support and ArgoCD multi-source secrets repo ([1aad047](https://github.com/meappy/kumon-marker/commit/1aad04738cb25c6fea5fa1039122cfd58233dd2d))
* initial commit with full application ([dc7dff2](https://github.com/meappy/kumon-marker/commit/dc7dff28ecd14a07dce7a97041fed2db18fb6766))
* move allowed users to private secrets repo ([48de9e3](https://github.com/meappy/kumon-marker/commit/48de9e3ef20aaf6c453f467d191c8efb14dc24be))
* move ArgoCD webhook URL to GitHub secrets ([0c154ed](https://github.com/meappy/kumon-marker/commit/0c154ed20e01892dbba2030800060d1b9339bba8))
* move ingress host and internal IPs to private secrets repo ([f3f43d4](https://github.com/meappy/kumon-marker/commit/f3f43d43d45ff4fb78f4bd7f73c7ed4f2c48c5bf))
* refactor to pluggable multi-provider architecture ([e2544b9](https://github.com/meappy/kumon-marker/commit/e2544b96f97b64aeae2f9f05f521f008996ee8b4))
* switch from Claude CLI to API mode ([93f1857](https://github.com/meappy/kumon-marker/commit/93f1857cf39c3264d152377294451684cecd915d))
* use claude-opus-4-6 model for worksheet analysis ([6bc171e](https://github.com/meappy/kumon-marker/commit/6bc171e0817e519418d0314130172313867c511d))
* use Tesseract OCR for sheet ID extraction ([e980490](https://github.com/meappy/kumon-marker/commit/e980490d4c39e8f6187502043b3e1d79e706df74))


### Performance Improvements

* extract sheet_id from filename first, skip download if valid ([d6ed871](https://github.com/meappy/kumon-marker/commit/d6ed8712f1d5dfdb8d82fa0f7a81622e41d939f8))

## [1.0.3](https://github.com/meappy/kumon-marker/compare/v1.0.2...v1.0.3) (2026-03-08)


### Bug Fixes

* unify branding with consistent SVG logo across all assets ([#21](https://github.com/meappy/kumon-marker/issues/21))

## [1.0.2](https://github.com/meappy/kumon-marker/compare/v1.0.1...v1.0.2) (2026-03-08)


### Bug Fixes

* replace emoji placeholders with actual logo branding ([#20](https://github.com/meappy/kumon-marker/issues/20))

## [1.0.1](https://github.com/meappy/kumon-marker/compare/v1.0.0...v1.0.1) (2026-03-08)


### Bug Fixes

* replace banner with dark navy background for dark mode

# 1.0.0 (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3))
* add quick text-layer check to filter non-Kumon PDFs
* add values-local.yaml.example template and security improvements
* build multi-platform Docker images (amd64 + arm64)
* capture semantic-release output for Docker build trigger
* clear validation cache when refresh is clicked
* correct sheet_id matching logic in GDriveModal
* extract sheet_id from PDF text layer during refresh
* force revalidation when refresh is clicked
* improve error handling for Google Drive API responses
* improve error messages for Google Drive connection issues
* improve Google Drive file matching and add validation caching
* improve OCR accuracy with image pre-processing
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1))
* improve sheet ID and topic extraction from worksheets
* log model name alongside vision provider in worker
* make applicationset.yaml a generic template
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6))
* prevent HTTPException from being caught by generic exception handler
* reduce memory requests to 512Mi for scheduling
* refresh now re-extracts sheet_ids instead of using cache
* regex pattern now matches uppercase A/B suffix after .upper()
* remove unused import
* resolve lint errors in backend and frontend
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9))
* run Google Drive scan in thread pool to prevent health check timeouts
* separate refresh (fast) from revalidate (slow) for GDrive files
* session cookie secure flag and OAuth scope mismatch
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon
* store PKCE code_verifier in signed cookie for OAuth callback
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5))
* update branding with white outlines for dark mode support
* update release workflow permissions for ghcr.io
* use filename for sheet_id extraction, simplify OCR
* use vision model instead of unreliable Tesseract OCR for validation
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8))


### Features

* add branding assets and update README
* add GitOps CI/CD with Semantic Release and Argo CD
* add graceful shutdown for worker to complete in-progress jobs
* add group-by-student option for worksheet list
* add ingress template and enable for production domain
* add MIT license and fix banner for dark mode
* add pre-commit hook for branch protection and linting
* add Revalidate button to GDrive modal
* add user to allowed users list
* auto-deploy branches via Argo CD
* dual secret support and ArgoCD multi-source secrets repo
* initial commit with full application
* move allowed users to private secrets repo
* move ArgoCD webhook URL to GitHub secrets
* move ingress host and internal IPs to private secrets repo
* refactor to pluggable multi-provider architecture
* switch from Claude CLI to API mode
* use claude-opus-4-6 model for worksheet analysis
* use Tesseract OCR for sheet ID extraction


### Performance Improvements

* extract sheet_id from filename first, skip download if valid

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3))
* add quick text-layer check to filter non-Kumon PDFs
* capture semantic-release output for Docker build trigger
* clear validation cache when refresh is clicked
* correct sheet_id matching logic in GDriveModal
* extract sheet_id from PDF text layer during refresh
* force revalidation when refresh is clicked
* improve error handling for Google Drive API responses
* improve error messages for Google Drive connection issues
* improve Google Drive file matching and add validation caching
* improve OCR accuracy with image pre-processing
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1))
* improve sheet ID and topic extraction from worksheets
* log model name alongside vision provider in worker
* make applicationset.yaml a generic template
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6))
* prevent HTTPException from being caught by generic exception handler
* reduce memory requests to 512Mi for scheduling
* refresh now re-extracts sheet_ids instead of using cache
* regex pattern now matches uppercase A/B suffix after .upper()
* remove unused import
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9))
* run Google Drive scan in thread pool to prevent health check timeouts
* separate refresh (fast) from revalidate (slow) for GDrive files
* session cookie secure flag and OAuth scope mismatch
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon
* store PKCE code_verifier in signed cookie for OAuth callback
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5))
* update branding with white outlines for dark mode support
* use filename for sheet_id extraction, simplify OCR
* use vision model instead of unreliable Tesseract OCR for validation
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8))


### Features

* add branding assets and update README
* add graceful shutdown for worker to complete in-progress jobs
* add group-by-student option for worksheet list
* add ingress template and enable for production domain
* add MIT license and fix banner for dark mode
* add pre-commit hook for branch protection and linting
* add Revalidate button to GDrive modal
* add user to allowed users list
* dual secret support and ArgoCD multi-source secrets repo
* move allowed users to private secrets repo
* move ArgoCD webhook URL to GitHub secrets
* move ingress host and internal IPs to private secrets repo
* refactor to pluggable multi-provider architecture
* switch from Claude CLI to API mode
* use claude-opus-4-6 model for worksheet analysis
* use Tesseract OCR for sheet ID extraction


### Performance Improvements

* extract sheet_id from filename first, skip download if valid

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3))
* add quick text-layer check to filter non-Kumon PDFs
* capture semantic-release output for Docker build trigger
* clear validation cache when refresh is clicked
* correct sheet_id matching logic in GDriveModal
* extract sheet_id from PDF text layer during refresh
* force revalidation when refresh is clicked
* improve error handling for Google Drive API responses
* improve error messages for Google Drive connection issues
* improve Google Drive file matching and add validation caching
* improve OCR accuracy with image pre-processing
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1))
* improve sheet ID and topic extraction from worksheets
* log model name alongside vision provider in worker
* make applicationset.yaml a generic template
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6))
* prevent HTTPException from being caught by generic exception handler
* reduce memory requests to 512Mi for scheduling
* refresh now re-extracts sheet_ids instead of using cache
* regex pattern now matches uppercase A/B suffix after .upper()
* remove unused import
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9))
* run Google Drive scan in thread pool to prevent health check timeouts
* separate refresh (fast) from revalidate (slow) for GDrive files
* session cookie secure flag and OAuth scope mismatch
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon
* store PKCE code_verifier in signed cookie for OAuth callback
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5))
* update branding with white outlines for dark mode support
* use filename for sheet_id extraction, simplify OCR
* use vision model instead of unreliable Tesseract OCR for validation
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8))


### Features

* add branding assets and update README
* add graceful shutdown for worker to complete in-progress jobs
* add group-by-student option for worksheet list
* add ingress template and enable for production domain
* add pre-commit hook for branch protection and linting
* add Revalidate button to GDrive modal
* add user to allowed users list
* dual secret support and ArgoCD multi-source secrets repo
* move allowed users to private secrets repo
* move ArgoCD webhook URL to GitHub secrets
* move ingress host and internal IPs to private secrets repo
* refactor to pluggable multi-provider architecture
* switch from Claude CLI to API mode
* use claude-opus-4-6 model for worksheet analysis
* use Tesseract OCR for sheet ID extraction


### Performance Improvements

* extract sheet_id from filename first, skip download if valid

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3))
* add quick text-layer check to filter non-Kumon PDFs
* capture semantic-release output for Docker build trigger
* clear validation cache when refresh is clicked
* correct sheet_id matching logic in GDriveModal
* extract sheet_id from PDF text layer during refresh
* force revalidation when refresh is clicked
* improve error handling for Google Drive API responses
* improve error messages for Google Drive connection issues
* improve Google Drive file matching and add validation caching
* improve OCR accuracy with image pre-processing
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1))
* improve sheet ID and topic extraction from worksheets
* log model name alongside vision provider in worker
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6))
* prevent HTTPException from being caught by generic exception handler
* reduce memory requests to 512Mi for scheduling
* refresh now re-extracts sheet_ids instead of using cache
* regex pattern now matches uppercase A/B suffix after .upper()
* remove unused import
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9))
* run Google Drive scan in thread pool to prevent health check timeouts
* separate refresh (fast) from revalidate (slow) for GDrive files
* session cookie secure flag and OAuth scope mismatch
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon
* store PKCE code_verifier in signed cookie for OAuth callback
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5))
* use filename for sheet_id extraction, simplify OCR
* use vision model instead of unreliable Tesseract OCR for validation
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8))


### Features

* add branding assets and update README
* add graceful shutdown for worker to complete in-progress jobs
* add group-by-student option for worksheet list
* add ingress template and enable for production domain
* add pre-commit hook for branch protection and linting
* add Revalidate button to GDrive modal
* add user to allowed users list
* dual secret support and ArgoCD multi-source secrets repo
* move allowed users to private secrets repo
* move ingress host and internal IPs to private secrets repo
* refactor to pluggable multi-provider architecture
* switch from Claude CLI to API mode
* use claude-opus-4-6 model for worksheet analysis
* use Tesseract OCR for sheet ID extraction


### Performance Improvements

* extract sheet_id from filename first, skip download if valid

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3))
* add quick text-layer check to filter non-Kumon PDFs
* capture semantic-release output for Docker build trigger
* clear validation cache when refresh is clicked
* correct sheet_id matching logic in GDriveModal
* extract sheet_id from PDF text layer during refresh
* force revalidation when refresh is clicked
* improve error handling for Google Drive API responses
* improve error messages for Google Drive connection issues
* improve Google Drive file matching and add validation caching
* improve OCR accuracy with image pre-processing
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1))
* improve sheet ID and topic extraction from worksheets
* log model name alongside vision provider in worker
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6))
* prevent HTTPException from being caught by generic exception handler
* reduce memory requests to 512Mi for scheduling
* refresh now re-extracts sheet_ids instead of using cache
* regex pattern now matches uppercase A/B suffix after .upper()
* remove unused import
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9))
* run Google Drive scan in thread pool to prevent health check timeouts
* separate refresh (fast) from revalidate (slow) for GDrive files
* session cookie secure flag and OAuth scope mismatch
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon
* store PKCE code_verifier in signed cookie for OAuth callback
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5))
* use filename for sheet_id extraction, simplify OCR
* use vision model instead of unreliable Tesseract OCR for validation
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8))


### Features

* add graceful shutdown for worker to complete in-progress jobs
* add group-by-student option for worksheet list
* add ingress template and enable for production domain
* add pre-commit hook for branch protection and linting
* add Revalidate button to GDrive modal
* add user to allowed users list
* dual secret support and ArgoCD multi-source secrets repo
* move allowed users to private secrets repo
* move ingress host and internal IPs to private secrets repo
* refactor to pluggable multi-provider architecture
* switch from Claude CLI to API mode
* use claude-opus-4-6 model for worksheet analysis
* use Tesseract OCR for sheet ID extraction


### Performance Improvements

* extract sheet_id from filename first, skip download if valid

## [0.6.2](https://github.com/meappy/kumon-marker/compare/v0.6.1...v0.6.2) (2026-01-25)


### Bug Fixes

* improve Google Drive file matching and add validation caching

## [0.6.1](https://github.com/meappy/kumon-marker/compare/v0.6.0...v0.6.1) (2026-01-25)


### Bug Fixes

* session cookie secure flag and OAuth scope mismatch

# [0.6.0](https://github.com/meappy/kumon-marker/compare/v0.5.3...v0.6.0) (2026-01-19)


### Features

* add user to allowed users

## [0.5.3](https://github.com/meappy/kumon-marker/compare/v0.5.2...v0.5.3) (2026-01-19)


### Bug Fixes

* prevent HTTPException from being caught by generic exception handler

## [0.5.2](https://github.com/meappy/kumon-marker/compare/v0.5.1...v0.5.2) (2026-01-19)


### Bug Fixes

* improve error messages for Google Drive connection issues

## [0.5.1](https://github.com/meappy/kumon-marker/compare/v0.5.0...v0.5.1) (2026-01-18)


### Bug Fixes

* run Google Drive scan in thread pool to prevent health check timeouts

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.12...v0.5.0) (2026-01-18)


### Features

* add graceful shutdown for worker to complete in-progress jobs

## [0.4.12](https://github.com/meappy/kumon-marker/compare/v0.4.11...v0.4.12) (2026-01-18)


### Bug Fixes

* improve error handling for Google Drive API responses

## [0.4.11](https://github.com/meappy/kumon-marker/compare/v0.4.10...v0.4.11) (2026-01-18)


### Bug Fixes

* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11))

## [0.4.10](https://github.com/meappy/kumon-marker/compare/v0.4.9...v0.4.10) (2026-01-18)


### Bug Fixes

* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10))

## [0.4.9](https://github.com/meappy/kumon-marker/compare/v0.4.8...v0.4.9) (2026-01-18)


### Bug Fixes

* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9))

## [0.4.8](https://github.com/meappy/kumon-marker/compare/v0.4.7...v0.4.8) (2026-01-18)


### Bug Fixes

* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8))

## [0.4.7](https://github.com/meappy/kumon-marker/compare/v0.4.6...v0.4.7) (2026-01-18)


### Bug Fixes

* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6))

## [0.4.6](https://github.com/meappy/kumon-marker/compare/v0.4.5...v0.4.6) (2026-01-18)


### Bug Fixes

* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5))

## [0.4.5](https://github.com/meappy/kumon-marker/compare/v0.4.4...v0.4.5) (2026-01-18)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4))

## [0.4.4](https://github.com/meappy/kumon-marker/compare/v0.4.3...v0.4.4) (2026-01-18)


### Bug Fixes

* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3))

## [0.4.3](https://github.com/meappy/kumon-marker/compare/v0.4.2...v0.4.3) (2026-01-18)


### Bug Fixes

* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2))

## [0.4.2](https://github.com/meappy/kumon-marker/compare/v0.4.1...v0.4.2) (2026-01-18)


### Bug Fixes

* capture semantic-release output for Docker build trigger

## [0.4.1](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.4.1) (2026-01-18)


### Bug Fixes

* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1))

# [0.4.0](https://github.com/meappy/kumon-marker/compare/v0.3.0...v0.4.0) (2026-01-17)


### Features

* auto-deploy branches via Argo CD

# [0.3.0](https://github.com/meappy/kumon-marker/compare/v0.2.8...v0.3.0) (2026-01-17)


### Features

* add GitOps CI/CD with Semantic Release and Argo CD
