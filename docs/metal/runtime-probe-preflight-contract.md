# Runtime Probe Preflight & Read-Only Harness Contract

## 목적
H1mekaRTX Phase 3 단계의 런타임 프로브 사전 비침습(Read-only) 검증 규격과 하드웨어 제어권 매칭 사전 요구사항을 정의합니다.

## 결과 분류 규칙 (Classification)
본 단계의 모든 진단 결과와 리포트는 오직 아래 두 수준으로만 라벨링 및 보고되어야 합니다.
- `CLASSIFICATION_STATIC_CONTRACT`: 코드 수준 규격 검증 및 모의 계약 결과
- `CLASSIFICATION_RUNTIME_PROBE_PREFLIGHT`: 실제 장치 접근 전 소프트웨어/환경 사전 진단 상태

## 안전 수칙 (Safety Boundary)
- **BAR_MMIO_SUBMISSION_FORBIDDEN**: 실제 BAR 및 MMIO 어드레스 영역으로의 쓰기 행위, 하드웨어 리셋, GSP 펌웨어 로드 및 GPU 명령 제출(Command Submission)은 무조건 금지됩니다.
- 본 프리플라이트는 쓰기 작업이 없는 안전 상태에서 실행을 유지하는 것을 계약 목적으로 삼습니다.

## DriverKit / System-Extension 사전 요구조건 (DRIVERKIT_PREREQUISITES)
1. **PCI Matching Manifest**:
   - target_gpu: "NVIDIA RTX 5070" (Blackwell Architecture)
   - vendor_id: `0x10de`
   - device_id: `0x2f04`
   - io-pci-match: `0x2f0410de`
2. **Entitlements Requirements**:
   - PCI-DriverKit 사용을 위한 Apple Entitlement 승인 필요
   - System-Extension (dext) 활성화 사전 준비 계약 확인

## 미래 Compositor 검증 기준 (FUTURE_EVIDENCE_CHECKLIST)
사용자가 체감하는 부드러운 macOS 데스크톱 UI(투명도, 블러, Dock 애니메이션, 창 크기 변경 등) 성능 가속 경로 추적을 위한 증거 체크리스트입니다.
1. `WindowServer`가 RTX 5070 GPU에 Composition 워크로드를 실제 할당하는지 여부
2. `Core Animation` 프레임 딜리버리 타임 및 드롭 카운트 추적 경로 설계
3. `QuartzCore` 렌더 파이프라인에서 소프트웨어 렌더러가 아닌 가속 디바이스 인스턴스 매칭 여부
4. `Metal compositor` 폴백 디터런스(Deterrence) 검증 구조

## 계약 상태
- **PREFLIGHT_STAGE_3_CONTRACT_READY**: True
- **REAL_GPU_ACCELERATION_CLAIMED**: False (절대 허위 가속 주장을 하지 않음)
