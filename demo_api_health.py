"""
AIOS Demo: API Health Check + Auto Recovery

Real-world scenario: Monitor API endpoints and automatically recover from failures.

Scenario:
1. Check multiple API endpoints every 5 seconds
2. Detect failures (timeout, error response, etc.)
3. Auto-retry failed requests (up to 3 times)
4. Alert if still failing after retries
5. Log all checks and recovery attempts

This demonstrates:
- Periodic monitoring
- Auto-recovery logic
- Alert system
- Real-world reliability patterns
"""
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add AIOS to path
AIOS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(AIOS_ROOT))


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    endpoint: str
    status: str  # "healthy", "degraded", "down"
    response_time_ms: float
    status_code: Optional[int]
    error: Optional[str]
    timestamp: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class APIEndpoint:
    """API endpoint configuration."""
    name: str
    url: str
    method: str = "GET"
    timeout: float = 5.0
    expected_status: int = 200
    max_retries: int = 3
    retry_delay: float = 1.0


class APIHealthChecker:
    """Monitor API health and auto-recover from failures."""
    
    def __init__(self, endpoints: List[APIEndpoint], log_file: Path):
        self.endpoints = endpoints
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Track failure counts
        self._failure_counts: Dict[str, int] = {ep.name: 0 for ep in endpoints}
        self._last_status: Dict[str, str] = {ep.name: "unknown" for ep in endpoints}
    
    def check_endpoint(self, endpoint: APIEndpoint) -> HealthCheckResult:
        """Check a single endpoint."""
        start_time = time.time()
        
        # Simulate API call (in real scenario, use requests library)
        # For demo, we'll simulate different scenarios
        import random
        
        # 80% success, 15% slow, 5% failure
        rand = random.random()
        
        if rand < 0.80:
            # Success
            response_time = random.uniform(50, 200)
            time.sleep(response_time / 1000)  # Simulate network delay
            
            result = HealthCheckResult(
                endpoint=endpoint.name,
                status="healthy",
                response_time_ms=response_time,
                status_code=200,
                error=None,
                timestamp=time.time(),
            )
        
        elif rand < 0.95:
            # Slow response (degraded)
            response_time = random.uniform(1000, 2000)  # 1-2s instead of 3-5s
            time.sleep(response_time / 1000)
            
            result = HealthCheckResult(
                endpoint=endpoint.name,
                status="degraded",
                response_time_ms=response_time,
                status_code=200,
                error="Slow response",
                timestamp=time.time(),
            )
        
        else:
            # Failure
            result = HealthCheckResult(
                endpoint=endpoint.name,
                status="down",
                response_time_ms=(time.time() - start_time) * 1000,
                status_code=None,
                error="Connection timeout",
                timestamp=time.time(),
            )
        
        return result
    
    def check_with_retry(self, endpoint: APIEndpoint) -> HealthCheckResult:
        """Check endpoint with automatic retry."""
        for attempt in range(endpoint.max_retries):
            result = self.check_endpoint(endpoint)
            
            if result.status == "healthy":
                # Success, reset failure count
                self._failure_counts[endpoint.name] = 0
                return result
            
            # Failed, increment counter
            self._failure_counts[endpoint.name] += 1
            
            if attempt < endpoint.max_retries - 1:
                print(f"  [Retry {attempt + 1}/{endpoint.max_retries - 1}] {endpoint.name} failed, retrying in {endpoint.retry_delay}s...")
                time.sleep(endpoint.retry_delay)
        
        return result
    
    def check_all(self) -> List[HealthCheckResult]:
        """Check all endpoints."""
        results = []
        
        for endpoint in self.endpoints:
            print(f"[Check] {endpoint.name} ({endpoint.url})")
            result = self.check_with_retry(endpoint)
            
            # Log result
            self._log_result(result)
            
            # Check for status change
            old_status = self._last_status[endpoint.name]
            new_status = result.status
            
            if old_status != new_status:
                self._handle_status_change(endpoint.name, old_status, new_status)
            
            self._last_status[endpoint.name] = new_status
            results.append(result)
            
            # Print result
            if result.status == "healthy":
                print(f"  ✓ Healthy ({result.response_time_ms:.0f}ms)")
            elif result.status == "degraded":
                print(f"  ⚠ Degraded ({result.response_time_ms:.0f}ms) - {result.error}")
            else:
                print(f"  ✗ Down - {result.error}")
        
        return results
    
    def _log_result(self, result: HealthCheckResult):
        """Log check result."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
    
    def _handle_status_change(self, endpoint_name: str, old_status: str, new_status: str):
        """Handle status change (recovery or degradation)."""
        if new_status == "healthy" and old_status in ["degraded", "down"]:
            print(f"  🎉 {endpoint_name} recovered! ({old_status} → {new_status})")
        elif new_status in ["degraded", "down"] and old_status == "healthy":
            print(f"  ⚠️  {endpoint_name} degraded! ({old_status} → {new_status})")
    
    def get_summary(self) -> Dict[str, any]:
        """Get health summary."""
        healthy = sum(1 for status in self._last_status.values() if status == "healthy")
        degraded = sum(1 for status in self._last_status.values() if status == "degraded")
        down = sum(1 for status in self._last_status.values() if status == "down")
        
        return {
            "total": len(self.endpoints),
            "healthy": healthy,
            "degraded": degraded,
            "down": down,
            "failure_counts": self._failure_counts.copy(),
        }


def main():
    """Run the demo."""
    print("=" * 70)
    print("AIOS Demo: API Health Check + Auto Recovery")
    print("=" * 70)
    print("\nScenario:")
    print("  1. Check multiple API endpoints every 2 seconds")
    print("  2. Detect failures (timeout, error response, etc.)")
    print("  3. Auto-retry failed requests (up to 3 times)")
    print("  4. Alert if still failing after retries")
    print("  5. Log all checks and recovery attempts")
    print("\nThis demonstrates:")
    print("  - Periodic monitoring")
    print("  - Auto-recovery logic")
    print("  - Alert system")
    print("  - Real-world reliability patterns")
    print("=" * 70)
    
    # Setup
    demo_dir = AIOS_ROOT / "demo_data" / "api_health"
    log_file = demo_dir / "health_checks.log"
    
    # Clean up previous demo
    if demo_dir.exists():
        import shutil
        shutil.rmtree(demo_dir)
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # Define endpoints to monitor
    endpoints = [
        APIEndpoint(name="API Gateway", url="https://api.example.com/health"),
        APIEndpoint(name="Database", url="https://db.example.com/ping"),
        APIEndpoint(name="Cache", url="https://cache.example.com/status"),
        APIEndpoint(name="Storage", url="https://storage.example.com/health"),
    ]
    
    # Initialize checker
    checker = APIHealthChecker(endpoints, log_file)
    
    print(f"\n[Setup] Monitoring {len(endpoints)} endpoints")
    print(f"  Log file: {log_file}")
    
    # Run checks (simulate 3 rounds)
    print("\n" + "=" * 70)
    print("Running health checks (3 rounds, 2s interval)...")
    print("=" * 70)
    
    for round_num in range(1, 4):
        print(f"\n[Round {round_num}/3] {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 70)
        
        results = checker.check_all()
        
        # Show summary
        summary = checker.get_summary()
        print(f"\nSummary: {summary['healthy']}/{summary['total']} healthy, "
              f"{summary['degraded']} degraded, {summary['down']} down")
        
        if round_num < 3:
            print("\nWaiting 2 seconds...")
            time.sleep(2)
    
    # Final summary
    print("\n" + "=" * 70)
    print("Final Summary:")
    print("=" * 70)
    
    summary = checker.get_summary()
    print(f"\nEndpoints: {summary['total']}")
    print(f"  ✓ Healthy: {summary['healthy']}")
    print(f"  ⚠ Degraded: {summary['degraded']}")
    print(f"  ✗ Down: {summary['down']}")
    
    print("\nFailure counts:")
    for endpoint, count in summary['failure_counts'].items():
        if count > 0:
            print(f"  {endpoint}: {count} failures")
    
    # Show log stats
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        print(f"\nTotal checks logged: {len(lines)}")
    
    print("\n" + "=" * 70)
    print("Demo completed! ✓")
    print("=" * 70)
    print(f"\nDemo files saved to: {demo_dir}")
    print("You can inspect the health check log for detailed results.")


if __name__ == "__main__":
    main()
