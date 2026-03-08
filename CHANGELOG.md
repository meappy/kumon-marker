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
