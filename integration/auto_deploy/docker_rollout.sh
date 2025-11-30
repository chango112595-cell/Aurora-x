#!/usr/bin/env bash
set -euo pipefail
# Usage: docker_rollout.sh <image:tag> <strategy: immediate|canary|staged> [staged_percent]
IMAGE="$1"
STRATEGY="${2:-immediate}"
PERCENT="${3:-10}"
REGISTRY="${REGISTRY:-yourregistry}"
# push image
echo "Pushing image $IMAGE"
docker push "$IMAGE"
if [[ "$STRATEGY" == "immediate" ]]; then
  echo "Immediate rollout: apply deployment update"
  kubectl set image deploy/auroraos auroraos="$IMAGE" --record || true
elif [[ "$STRATEGY" == "canary" ]]; then
  echo "Canary: create canary deployment auroraos-canary"
  kubectl set image deployment/auroraos-canary auroraos="$IMAGE" --record || true
elif [[ "$STRATEGY" == "staged" ]]; then
  echo "Staged rollout placeholder: you must configure traffic splitting (service mesh) or deploy to subset nodes."
  echo "Staged percent requested: $PERCENT"
fi
