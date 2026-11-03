#include <iostream>

int find_pair(int limit) {
  int found = -1;
  for (int i = 0; i < limit; ++i) {
    for (int j = 0; j < limit; ++j) {
      if (i != j && (i + j) % 7 == 3) {
        found = i * 10 + j;
        goto search_done; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
      }
    }
  }
search_done:
  return found;
}

int main() {
  std::cout << find_pair(5) << '\n';
  return 0;
}
