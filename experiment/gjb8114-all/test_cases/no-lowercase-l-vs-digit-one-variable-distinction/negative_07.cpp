#include <cstdio>

int main() {
  int total = 0;
  for (int fSpeedsl = 0, fSpeeds1 = 1; fSpeedsl < 3; ++fSpeedsl)  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
  {
    total += fSpeeds1;
  }
  std::printf("%d\n", total);
  return 0;
}
