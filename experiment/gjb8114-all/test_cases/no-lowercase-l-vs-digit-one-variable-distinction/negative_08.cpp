#include <cstdio>

int main() {
  auto counterl = 4;
  auto counter1 = 7;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
  std::printf("%d\n", counterl + counter1);
  return 0;
}
