## [1.0.3](https://github.com/meappy/kumon-marker/compare/v1.0.2...v1.0.3) (2026-03-08)


### Bug Fixes

* unify branding with consistent SVG logo across all assets ([#21](https://github.com/meappy/kumon-marker/issues/21)) ([36afe3c](https://github.com/meappy/kumon-marker/commit/36afe3c90b38db9c46aab9dc17177a2c53d6a429))

## [1.0.2](https://github.com/meappy/kumon-marker/compare/v1.0.1...v1.0.2) (2026-03-08)


### Bug Fixes

* replace emoji placeholders with actual logo branding ([#20](https://github.com/meappy/kumon-marker/issues/20)) ([aafd427](https://github.com/meappy/kumon-marker/commit/aafd427cff93bd8fb5a255488c2f995d0db938d5))

## [1.0.1](https://github.com/meappy/kumon-marker/compare/v1.0.0...v1.0.1) (2026-03-08)


### Bug Fixes

* replace banner with dark navy background for dark mode ([aac8a35](https://github.com/meappy/kumon-marker/commit/aac8a35d14f4940d4c45d1006253babd5b9ed4e8))

# 1.0.0 (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([47817db](https://github.com/meappy/kumon-marker/commit/47817db79277346b27db8f77d63ec31edded9db7))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([4eb817f](https://github.com/meappy/kumon-marker/commit/4eb817fa5b1ecfad85779a4cfe22244a7b6f1b89))
* add quick text-layer check to filter non-Kumon PDFs ([97482f7](https://github.com/meappy/kumon-marker/commit/97482f726b0f029a9d652a53be6a182e9b387ae5))
* add values-local.yaml.example template and security improvements ([8f3b9e5](https://github.com/meappy/kumon-marker/commit/8f3b9e5e5c47dd08e4ce16d81be83a2d5b9e9b8a))
* build multi-platform Docker images (amd64 + arm64) ([c0ccbab](https://github.com/meappy/kumon-marker/commit/c0ccbab24e605c3e6299c71f40fd51d13ee3bb6b))
* capture semantic-release output for Docker build trigger ([8205c2e](https://github.com/meappy/kumon-marker/commit/8205c2e23adbbbaf52924b0709a6d52721c9544f))
* clear validation cache when refresh is clicked ([01919c6](https://github.com/meappy/kumon-marker/commit/01919c67652417c7220e87cae3f3cd779e87dcba))
* correct sheet_id matching logic in GDriveModal ([a427a3e](https://github.com/meappy/kumon-marker/commit/a427a3e7aa9421053fee9b714a923e3cc488ac69))
* extract sheet_id from PDF text layer during refresh ([a74b969](https://github.com/meappy/kumon-marker/commit/a74b96920ae42c84b33203dbf2b36a9b26f965a3))
* force revalidation when refresh is clicked ([74e7dce](https://github.com/meappy/kumon-marker/commit/74e7dce6d427d05cbac9cd9f6c0d99dd97445901))
* improve error handling for Google Drive API responses ([9e112b9](https://github.com/meappy/kumon-marker/commit/9e112b9eedeb0a5ddde9b152f9e4fe27ed8eb5e9))
* improve error messages for Google Drive connection issues ([20ed824](https://github.com/meappy/kumon-marker/commit/20ed824ef65d104ee0023b47e6df81a63dbded1e))
* improve Google Drive file matching and add validation caching ([218fdb4](https://github.com/meappy/kumon-marker/commit/218fdb4d150e6883d21912b5c82ac8fc338e13d4))
* improve OCR accuracy with image pre-processing ([d4b2fe8](https://github.com/meappy/kumon-marker/commit/d4b2fe81d9b8483d0f9448474b16fd715a755871))
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([2893278](https://github.com/meappy/kumon-marker/commit/28932780c71dd11f534965e88c9c2102ce594b1b))
* improve sheet ID and topic extraction from worksheets ([677409e](https://github.com/meappy/kumon-marker/commit/677409e4594d2c8b7ec304fd6f62e343ebb79942))
* log model name alongside vision provider in worker ([d7a7212](https://github.com/meappy/kumon-marker/commit/d7a7212a6e9aa4bea501b429061c09e5607e04f7))
* make applicationset.yaml a generic template ([22784c8](https://github.com/meappy/kumon-marker/commit/22784c8614ad89311ba2f0d9c92c047d5e32974a))
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([d24e59a](https://github.com/meappy/kumon-marker/commit/d24e59a62b1533f1bda94a7d4f1e747245fb4359))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([8204a0e](https://github.com/meappy/kumon-marker/commit/8204a0ec5de99a00589f20a21beb4428b1937fdc))
* prevent HTTPException from being caught by generic exception handler ([f780563](https://github.com/meappy/kumon-marker/commit/f780563098c7bf79750607673edafa31543039cf))
* reduce memory requests to 512Mi for scheduling ([ac28c4d](https://github.com/meappy/kumon-marker/commit/ac28c4d6a655619ef7c11f8a0b79bf8103a29924))
* refresh now re-extracts sheet_ids instead of using cache ([c7a9258](https://github.com/meappy/kumon-marker/commit/c7a9258a8c45b7675a809052ad0791b6f894f560))
* regex pattern now matches uppercase A/B suffix after .upper() ([ac79ecb](https://github.com/meappy/kumon-marker/commit/ac79ecbe6b955776bd274cf60da42e5c948a92ad))
* remove unused import ([ebd92a8](https://github.com/meappy/kumon-marker/commit/ebd92a83e50c04d7037d7c9557ccf0a2928b2409))
* resolve lint errors in backend and frontend ([abddb84](https://github.com/meappy/kumon-marker/commit/abddb84a0872b272d53753b92ae7163c00f0020b))
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([641bba6](https://github.com/meappy/kumon-marker/commit/641bba603ce4ba959e911ac503c84b1a340f3025))
* run Google Drive scan in thread pool to prevent health check timeouts ([9f22d84](https://github.com/meappy/kumon-marker/commit/9f22d84bdf22060140f7202f96ebeafc9ad2e5e7))
* separate refresh (fast) from revalidate (slow) for GDrive files ([261eeb9](https://github.com/meappy/kumon-marker/commit/261eeb9bd52dc2ecf224fb305ae16f1fca6fbca3))
* session cookie secure flag and OAuth scope mismatch ([359db6c](https://github.com/meappy/kumon-marker/commit/359db6c11f69e9de310b2faa7b5350114982ac59))
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([c0ce47b](https://github.com/meappy/kumon-marker/commit/c0ce47bc5c7ab88cd178201ec1284293056f2168))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon ([8eba0d8](https://github.com/meappy/kumon-marker/commit/8eba0d85f71da5d79cfca120bf7109a548fa3056))
* store PKCE code_verifier in signed cookie for OAuth callback ([56312f3](https://github.com/meappy/kumon-marker/commit/56312f3eca27446d65cce7515202cfded44fa2d6))
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([021b1fb](https://github.com/meappy/kumon-marker/commit/021b1fbad73f55d13ec87e534a8e9b1cb7f47c19))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([7354aa4](https://github.com/meappy/kumon-marker/commit/7354aa4ea712303b89d3a036a64f7d20f90133d0))
* update branding with white outlines for dark mode support ([8adb3d5](https://github.com/meappy/kumon-marker/commit/8adb3d51910d54cabd5570e708d65b9eb61014ad))
* update release workflow permissions for ghcr.io ([079dbf5](https://github.com/meappy/kumon-marker/commit/079dbf5da9be6564368a31c89601b6523ddf41e0))
* use filename for sheet_id extraction, simplify OCR ([8868d94](https://github.com/meappy/kumon-marker/commit/8868d949c6cdd6cb9538473ba59d1c2258b39e72))
* use vision model instead of unreliable Tesseract OCR for validation ([21a99b2](https://github.com/meappy/kumon-marker/commit/21a99b2c0b0c3d336f09332b8bf517ad5cbee0a7))
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([087052f](https://github.com/meappy/kumon-marker/commit/087052f3b89de9ad9b3a1df1c45342e81e2b23b2))


### Features

* add branding assets and update README ([9813591](https://github.com/meappy/kumon-marker/commit/9813591713eb1167b752bcc41ca37c1f61ea2f3e))
* add GitOps CI/CD with Semantic Release and Argo CD ([3920d2b](https://github.com/meappy/kumon-marker/commit/3920d2b18dce4aab1365e26fe89859d252c1ec61))
* add graceful shutdown for worker to complete in-progress jobs ([8c76fdb](https://github.com/meappy/kumon-marker/commit/8c76fdbf97c8d4f6b2e11bf5df1b8225c1aa3116))
* add group-by-student option for worksheet list ([ea7b5a8](https://github.com/meappy/kumon-marker/commit/ea7b5a86da5dd73d126c2e4de7f38590f73b09ea))
* add ingress template and enable for production domain ([d246b10](https://github.com/meappy/kumon-marker/commit/d246b10238380b14287cdc5ae5f5063efdc4cbda))
* add MIT license and fix banner for dark mode ([c250800](https://github.com/meappy/kumon-marker/commit/c250800b12f7e34fd386fbb311f67d1cc73358df))
* add pre-commit hook for branch protection and linting ([25141a9](https://github.com/meappy/kumon-marker/commit/25141a921867652016ba9b910715b6b6da98fcb2))
* add Revalidate button to GDrive modal ([d858bc4](https://github.com/meappy/kumon-marker/commit/d858bc41088f8b5edd61d8d37cc6225487894032))
* add user to allowed users list ([d6d137a](https://github.com/meappy/kumon-marker/commit/d6d137acef6f480ac894f4fa7e649c9f3faeac11))
* auto-deploy branches via Argo CD ([3269e44](https://github.com/meappy/kumon-marker/commit/3269e44aca665f1d9ddd99d86fb164cdf1db60d9))
* dual secret support and ArgoCD multi-source secrets repo ([72a2f70](https://github.com/meappy/kumon-marker/commit/72a2f708f208d6d0a9e1804c9d0c6b1f9a21b829))
* initial commit with full application ([dc7dff2](https://github.com/meappy/kumon-marker/commit/dc7dff28ecd14a07dce7a97041fed2db18fb6766))
* move allowed users to private secrets repo ([fc69234](https://github.com/meappy/kumon-marker/commit/fc69234fb9a6854cfce6c5ce81c3c47cbda3392d))
* move ArgoCD webhook URL to GitHub secrets ([739232a](https://github.com/meappy/kumon-marker/commit/739232af1da563ed6903d2cd270165a37bfb0d2b))
* move ingress host and internal IPs to private secrets repo ([9091d42](https://github.com/meappy/kumon-marker/commit/9091d42a5c184e300e43e691720847cda75b81c3))
* refactor to pluggable multi-provider architecture ([55f20a1](https://github.com/meappy/kumon-marker/commit/55f20a13d78de3c7d8fdee4ea3e1178543b269c8))
* switch from Claude CLI to API mode ([f4bb542](https://github.com/meappy/kumon-marker/commit/f4bb542de105189c1fe489e03c6984eddc3dfad9))
* use claude-opus-4-6 model for worksheet analysis ([f846d69](https://github.com/meappy/kumon-marker/commit/f846d699ad9a0df5462ec3d33bb8d6d257ec262a))
* use Tesseract OCR for sheet ID extraction ([9aaaac0](https://github.com/meappy/kumon-marker/commit/9aaaac0329493cad79b8804873b1c1306207b844))


### Performance Improvements

* extract sheet_id from filename first, skip download if valid ([431d941](https://github.com/meappy/kumon-marker/commit/431d94171eb7980fb05da26785088b55f795b0c7))

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([47817db](https://github.com/meappy/kumon-marker/commit/47817db79277346b27db8f77d63ec31edded9db7))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([4eb817f](https://github.com/meappy/kumon-marker/commit/4eb817fa5b1ecfad85779a4cfe22244a7b6f1b89))
* add quick text-layer check to filter non-Kumon PDFs ([97482f7](https://github.com/meappy/kumon-marker/commit/97482f726b0f029a9d652a53be6a182e9b387ae5))
* capture semantic-release output for Docker build trigger ([8205c2e](https://github.com/meappy/kumon-marker/commit/8205c2e23adbbbaf52924b0709a6d52721c9544f))
* clear validation cache when refresh is clicked ([01919c6](https://github.com/meappy/kumon-marker/commit/01919c67652417c7220e87cae3f3cd779e87dcba))
* correct sheet_id matching logic in GDriveModal ([a427a3e](https://github.com/meappy/kumon-marker/commit/a427a3e7aa9421053fee9b714a923e3cc488ac69))
* extract sheet_id from PDF text layer during refresh ([a74b969](https://github.com/meappy/kumon-marker/commit/a74b96920ae42c84b33203dbf2b36a9b26f965a3))
* force revalidation when refresh is clicked ([74e7dce](https://github.com/meappy/kumon-marker/commit/74e7dce6d427d05cbac9cd9f6c0d99dd97445901))
* improve error handling for Google Drive API responses ([9e112b9](https://github.com/meappy/kumon-marker/commit/9e112b9eedeb0a5ddde9b152f9e4fe27ed8eb5e9))
* improve error messages for Google Drive connection issues ([20ed824](https://github.com/meappy/kumon-marker/commit/20ed824ef65d104ee0023b47e6df81a63dbded1e))
* improve Google Drive file matching and add validation caching ([218fdb4](https://github.com/meappy/kumon-marker/commit/218fdb4d150e6883d21912b5c82ac8fc338e13d4))
* improve OCR accuracy with image pre-processing ([d4b2fe8](https://github.com/meappy/kumon-marker/commit/d4b2fe81d9b8483d0f9448474b16fd715a755871))
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([2893278](https://github.com/meappy/kumon-marker/commit/28932780c71dd11f534965e88c9c2102ce594b1b))
* improve sheet ID and topic extraction from worksheets ([677409e](https://github.com/meappy/kumon-marker/commit/677409e4594d2c8b7ec304fd6f62e343ebb79942))
* log model name alongside vision provider in worker ([d7a7212](https://github.com/meappy/kumon-marker/commit/d7a7212a6e9aa4bea501b429061c09e5607e04f7))
* make applicationset.yaml a generic template ([22784c8](https://github.com/meappy/kumon-marker/commit/22784c8614ad89311ba2f0d9c92c047d5e32974a))
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([d24e59a](https://github.com/meappy/kumon-marker/commit/d24e59a62b1533f1bda94a7d4f1e747245fb4359))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([8204a0e](https://github.com/meappy/kumon-marker/commit/8204a0ec5de99a00589f20a21beb4428b1937fdc))
* prevent HTTPException from being caught by generic exception handler ([f780563](https://github.com/meappy/kumon-marker/commit/f780563098c7bf79750607673edafa31543039cf))
* reduce memory requests to 512Mi for scheduling ([ac28c4d](https://github.com/meappy/kumon-marker/commit/ac28c4d6a655619ef7c11f8a0b79bf8103a29924))
* refresh now re-extracts sheet_ids instead of using cache ([c7a9258](https://github.com/meappy/kumon-marker/commit/c7a9258a8c45b7675a809052ad0791b6f894f560))
* regex pattern now matches uppercase A/B suffix after .upper() ([ac79ecb](https://github.com/meappy/kumon-marker/commit/ac79ecbe6b955776bd274cf60da42e5c948a92ad))
* remove unused import ([ebd92a8](https://github.com/meappy/kumon-marker/commit/ebd92a83e50c04d7037d7c9557ccf0a2928b2409))
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([641bba6](https://github.com/meappy/kumon-marker/commit/641bba603ce4ba959e911ac503c84b1a340f3025))
* run Google Drive scan in thread pool to prevent health check timeouts ([9f22d84](https://github.com/meappy/kumon-marker/commit/9f22d84bdf22060140f7202f96ebeafc9ad2e5e7))
* separate refresh (fast) from revalidate (slow) for GDrive files ([261eeb9](https://github.com/meappy/kumon-marker/commit/261eeb9bd52dc2ecf224fb305ae16f1fca6fbca3))
* session cookie secure flag and OAuth scope mismatch ([359db6c](https://github.com/meappy/kumon-marker/commit/359db6c11f69e9de310b2faa7b5350114982ac59))
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([c0ce47b](https://github.com/meappy/kumon-marker/commit/c0ce47bc5c7ab88cd178201ec1284293056f2168))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon ([8eba0d8](https://github.com/meappy/kumon-marker/commit/8eba0d85f71da5d79cfca120bf7109a548fa3056))
* store PKCE code_verifier in signed cookie for OAuth callback ([56312f3](https://github.com/meappy/kumon-marker/commit/56312f3eca27446d65cce7515202cfded44fa2d6))
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([021b1fb](https://github.com/meappy/kumon-marker/commit/021b1fbad73f55d13ec87e534a8e9b1cb7f47c19))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([7354aa4](https://github.com/meappy/kumon-marker/commit/7354aa4ea712303b89d3a036a64f7d20f90133d0))
* update branding with white outlines for dark mode support ([8adb3d5](https://github.com/meappy/kumon-marker/commit/8adb3d51910d54cabd5570e708d65b9eb61014ad))
* use filename for sheet_id extraction, simplify OCR ([8868d94](https://github.com/meappy/kumon-marker/commit/8868d949c6cdd6cb9538473ba59d1c2258b39e72))
* use vision model instead of unreliable Tesseract OCR for validation ([21a99b2](https://github.com/meappy/kumon-marker/commit/21a99b2c0b0c3d336f09332b8bf517ad5cbee0a7))
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([087052f](https://github.com/meappy/kumon-marker/commit/087052f3b89de9ad9b3a1df1c45342e81e2b23b2))


### Features

* add branding assets and update README ([9813591](https://github.com/meappy/kumon-marker/commit/9813591713eb1167b752bcc41ca37c1f61ea2f3e))
* add graceful shutdown for worker to complete in-progress jobs ([8c76fdb](https://github.com/meappy/kumon-marker/commit/8c76fdbf97c8d4f6b2e11bf5df1b8225c1aa3116))
* add group-by-student option for worksheet list ([ea7b5a8](https://github.com/meappy/kumon-marker/commit/ea7b5a86da5dd73d126c2e4de7f38590f73b09ea))
* add ingress template and enable for production domain ([d246b10](https://github.com/meappy/kumon-marker/commit/d246b10238380b14287cdc5ae5f5063efdc4cbda))
* add MIT license and fix banner for dark mode ([864242b](https://github.com/meappy/kumon-marker/commit/864242b358796a6898b536880276e1448f8b421d))
* add pre-commit hook for branch protection and linting ([25141a9](https://github.com/meappy/kumon-marker/commit/25141a921867652016ba9b910715b6b6da98fcb2))
* add Revalidate button to GDrive modal ([d858bc4](https://github.com/meappy/kumon-marker/commit/d858bc41088f8b5edd61d8d37cc6225487894032))
* add user to allowed users list ([d6d137a](https://github.com/meappy/kumon-marker/commit/d6d137acef6f480ac894f4fa7e649c9f3faeac11))
* dual secret support and ArgoCD multi-source secrets repo ([72a2f70](https://github.com/meappy/kumon-marker/commit/72a2f708f208d6d0a9e1804c9d0c6b1f9a21b829))
* move allowed users to private secrets repo ([fc69234](https://github.com/meappy/kumon-marker/commit/fc69234fb9a6854cfce6c5ce81c3c47cbda3392d))
* move ArgoCD webhook URL to GitHub secrets ([739232a](https://github.com/meappy/kumon-marker/commit/739232af1da563ed6903d2cd270165a37bfb0d2b))
* move ingress host and internal IPs to private secrets repo ([9091d42](https://github.com/meappy/kumon-marker/commit/9091d42a5c184e300e43e691720847cda75b81c3))
* refactor to pluggable multi-provider architecture ([55f20a1](https://github.com/meappy/kumon-marker/commit/55f20a13d78de3c7d8fdee4ea3e1178543b269c8))
* switch from Claude CLI to API mode ([f4bb542](https://github.com/meappy/kumon-marker/commit/f4bb542de105189c1fe489e03c6984eddc3dfad9))
* use claude-opus-4-6 model for worksheet analysis ([f846d69](https://github.com/meappy/kumon-marker/commit/f846d699ad9a0df5462ec3d33bb8d6d257ec262a))
* use Tesseract OCR for sheet ID extraction ([9aaaac0](https://github.com/meappy/kumon-marker/commit/9aaaac0329493cad79b8804873b1c1306207b844))


### Performance Improvements

* extract sheet_id from filename first, skip download if valid ([431d941](https://github.com/meappy/kumon-marker/commit/431d94171eb7980fb05da26785088b55f795b0c7))

# [0.5.0](https://github.com/meappy/kumon-marker/compare/v0.4.0...v0.5.0) (2026-03-08)


### Bug Fixes

* add Argo CD webhook to CI workflow for dev deployments ([#4](https://github.com/meappy/kumon-marker/issues/4)) ([47817db](https://github.com/meappy/kumon-marker/commit/47817db79277346b27db8f77d63ec31edded9db7))
* add HMAC-SHA256 signature for Argo CD webhook ([#3](https://github.com/meappy/kumon-marker/issues/3)) ([4eb817f](https://github.com/meappy/kumon-marker/commit/4eb817fa5b1ecfad85779a4cfe22244a7b6f1b89))
* add quick text-layer check to filter non-Kumon PDFs ([97482f7](https://github.com/meappy/kumon-marker/commit/97482f726b0f029a9d652a53be6a182e9b387ae5))
* capture semantic-release output for Docker build trigger ([8205c2e](https://github.com/meappy/kumon-marker/commit/8205c2e23adbbbaf52924b0709a6d52721c9544f))
* clear validation cache when refresh is clicked ([01919c6](https://github.com/meappy/kumon-marker/commit/01919c67652417c7220e87cae3f3cd779e87dcba))
* correct sheet_id matching logic in GDriveModal ([a427a3e](https://github.com/meappy/kumon-marker/commit/a427a3e7aa9421053fee9b714a923e3cc488ac69))
* extract sheet_id from PDF text layer during refresh ([a74b969](https://github.com/meappy/kumon-marker/commit/a74b96920ae42c84b33203dbf2b36a9b26f965a3))
* force revalidation when refresh is clicked ([74e7dce](https://github.com/meappy/kumon-marker/commit/74e7dce6d427d05cbac9cd9f6c0d99dd97445901))
* improve error handling for Google Drive API responses ([9e112b9](https://github.com/meappy/kumon-marker/commit/9e112b9eedeb0a5ddde9b152f9e4fe27ed8eb5e9))
* improve error messages for Google Drive connection issues ([20ed824](https://github.com/meappy/kumon-marker/commit/20ed824ef65d104ee0023b47e6df81a63dbded1e))
* improve Google Drive file matching and add validation caching ([218fdb4](https://github.com/meappy/kumon-marker/commit/218fdb4d150e6883d21912b5c82ac8fc338e13d4))
* improve OCR accuracy with image pre-processing ([d4b2fe8](https://github.com/meappy/kumon-marker/commit/d4b2fe81d9b8483d0f9448474b16fd715a755871))
* improve scanned PDF validation with responsive UI ([#1](https://github.com/meappy/kumon-marker/issues/1)) ([2893278](https://github.com/meappy/kumon-marker/commit/28932780c71dd11f534965e88c9c2102ce594b1b))
* improve sheet ID and topic extraction from worksheets ([677409e](https://github.com/meappy/kumon-marker/commit/677409e4594d2c8b7ec304fd6f62e343ebb79942))
* log model name alongside vision provider in worker ([d7a7212](https://github.com/meappy/kumon-marker/commit/d7a7212a6e9aa4bea501b429061c09e5607e04f7))
* make applicationset.yaml a generic template ([22784c8](https://github.com/meappy/kumon-marker/commit/22784c8614ad89311ba2f0d9c92c047d5e32974a))
* move grade badge to own line on mobile ([#11](https://github.com/meappy/kumon-marker/issues/11)) ([d24e59a](https://github.com/meappy/kumon-marker/commit/d24e59a62b1533f1bda94a7d4f1e747245fb4359))
* prevent CI/Release workflow race condition ([#6](https://github.com/meappy/kumon-marker/issues/6)) ([8204a0e](https://github.com/meappy/kumon-marker/commit/8204a0ec5de99a00589f20a21beb4428b1937fdc))
* prevent HTTPException from being caught by generic exception handler ([f780563](https://github.com/meappy/kumon-marker/commit/f780563098c7bf79750607673edafa31543039cf))
* reduce memory requests to 512Mi for scheduling ([ac28c4d](https://github.com/meappy/kumon-marker/commit/ac28c4d6a655619ef7c11f8a0b79bf8103a29924))
* refresh now re-extracts sheet_ids instead of using cache ([c7a9258](https://github.com/meappy/kumon-marker/commit/c7a9258a8c45b7675a809052ad0791b6f894f560))
* regex pattern now matches uppercase A/B suffix after .upper() ([ac79ecb](https://github.com/meappy/kumon-marker/commit/ac79ecbe6b955776bd274cf60da42e5c948a92ad))
* remove unused import ([ebd92a8](https://github.com/meappy/kumon-marker/commit/ebd92a83e50c04d7037d7c9557ccf0a2928b2409))
* responsive grade badge - hide score on mobile ([#9](https://github.com/meappy/kumon-marker/issues/9)) ([641bba6](https://github.com/meappy/kumon-marker/commit/641bba603ce4ba959e911ac503c84b1a340f3025))
* run Google Drive scan in thread pool to prevent health check timeouts ([9f22d84](https://github.com/meappy/kumon-marker/commit/9f22d84bdf22060140f7202f96ebeafc9ad2e5e7))
* separate refresh (fast) from revalidate (slow) for GDrive files ([261eeb9](https://github.com/meappy/kumon-marker/commit/261eeb9bd52dc2ecf224fb305ae16f1fca6fbca3))
* session cookie secure flag and OAuth scope mismatch ([359db6c](https://github.com/meappy/kumon-marker/commit/359db6c11f69e9de310b2faa7b5350114982ac59))
* show score on separate line on mobile instead of tooltip ([#10](https://github.com/meappy/kumon-marker/issues/10)) ([c0ce47b](https://github.com/meappy/kumon-marker/commit/c0ce47bc5c7ab88cd178201ec1284293056f2168))
* simplify GDrive scan - skip validation, assume all PDFs are Kumon ([8eba0d8](https://github.com/meappy/kumon-marker/commit/8eba0d85f71da5d79cfca120bf7109a548fa3056))
* store PKCE code_verifier in signed cookie for OAuth callback ([56312f3](https://github.com/meappy/kumon-marker/commit/56312f3eca27446d65cce7515202cfded44fa2d6))
* UI alignment and Argo CD webhook trigger ([#2](https://github.com/meappy/kumon-marker/issues/2)) ([021b1fb](https://github.com/meappy/kumon-marker/commit/021b1fbad73f55d13ec87e534a8e9b1cb7f47c19))
* UI consistency and search filter ([#5](https://github.com/meappy/kumon-marker/issues/5)) ([7354aa4](https://github.com/meappy/kumon-marker/commit/7354aa4ea712303b89d3a036a64f7d20f90133d0))
* update branding with white outlines for dark mode support ([8adb3d5](https://github.com/meappy/kumon-marker/commit/8adb3d51910d54cabd5570e708d65b9eb61014ad))
* use filename for sheet_id extraction, simplify OCR ([8868d94](https://github.com/meappy/kumon-marker/commit/8868d949c6cdd6cb9538473ba59d1c2258b39e72))
* use vision model instead of unreliable Tesseract OCR for validation ([21a99b2](https://github.com/meappy/kumon-marker/commit/21a99b2c0b0c3d336f09332b8bf517ad5cbee0a7))
* workflow deadlock and consistent grade badge format ([#8](https://github.com/meappy/kumon-marker/issues/8)) ([087052f](https://github.com/meappy/kumon-marker/commit/087052f3b89de9ad9b3a1df1c45342e81e2b23b2))


### Features

* add branding assets and update README ([9813591](https://github.com/meappy/kumon-marker/commit/9813591713eb1167b752bcc41ca37c1f61ea2f3e))
* add graceful shutdown for worker to complete in-progress jobs ([8c76fdb](https://github.com/meappy/kumon-marker/commit/8c76fdbf97c8d4f6b2e11bf5df1b8225c1aa3116))
* add group-by-student option for worksheet list ([ea7b5a8](https://github.com/meappy/kumon-marker/commit/ea7b5a86da5dd73d126c2e4de7f38590f73b09ea))
* add ingress template and enable for production domain ([d246b10](https://github.com/meappy/kumon-marker/commit/d246b10238380b14287cdc5ae5f5063efdc4cbda))
* add pre-commit hook for branch protection and linting ([25141a9](https://github.com/meappy/kumon-marker/commit/25141a921867652016ba9b910715b6b6da98fcb2))
* add Revalidate button to GDrive modal ([d858bc4](https://github.com/meappy/kumon-marker/commit/d858bc41088f8b5edd61d8d37cc6225487894032))
* add user to allowed users list ([d6d137a](https://github.com/meappy/kumon-marker/commit/d6d137acef6f480ac894f4fa7e649c9f3faeac11))
* dual secret support and ArgoCD multi-source secrets repo ([72a2f70](https://github.com/meappy/kumon-marker/commit/72a2f708f208d6d0a9e1804c9d0c6b1f9a21b829))
* move allowed users to private secrets repo ([fc69234](https://github.com/meappy/kumon-marker/commit/fc69234fb9a6854cfce6c5ce81c3c47cbda3392d))
* move ArgoCD webhook URL to GitHub secrets ([739232a](https://github.com/meappy/kumon-marker/commit/739232af1da563ed6903d2cd270165a37bfb0d2b))
* move ingress host and internal IPs to private secrets repo ([9091d42](https://github.com/meappy/kumon-marker/commit/9091d42a5c184e300e43e691720847cda75b81c3))
* refactor to pluggable multi-provider architecture ([55f20a1](https://github.com/meappy/kumon-marker/commit/55f20a13d78de3c7d8fdee4ea3e1178543b269c8))
* switch from Claude CLI to API mode ([f4bb542](https://github.com/meappy/kumon-marker/commit/f4bb542de105189c1fe489e03c6984eddc3dfad9))
* use claude-opus-4-6 model for worksheet analysis ([f846d69](https://github.com/meappy/kumon-marker/commit/f846d699ad9a0df5462ec3d33bb8d6d257ec262a))
* use Tesseract OCR for sheet ID extraction ([9aaaac0](https://github.com/meappy/kumon-marker/commit/9aaaac0329493cad79b8804873b1c1306207b844))


### Performance Improvements

* extract sheet_id from filename first, skip download if valid ([431d941](https://github.com/meappy/kumon-marker/commit/431d94171eb7980fb05da26785088b55f795b0c7))

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

* add user to allowed users ([f102680](https://github.com/meappy/kumon-marker/commit/f102680dd93da8b54f68003d197d6f0cbe7364ce))

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
