#include <vector>

int process(const std::vector<int>& values) {
  int result = 0;
  for (int i = 0; i < static_cast<int>(values.size()); ++i) {
    if (values[i] == 0) {
      goto after_loop; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
    }
    result += values[i];
  }
after_loop:
  result += 10;
  return result;
}
