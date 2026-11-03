#include <vector>

int main() {
  std::vector<int> const values{1, 2, 3}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
  return values.size() == 3 ? 0 : 1;
}
