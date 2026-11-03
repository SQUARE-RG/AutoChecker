#include <cstdio>

int main() {
  int total = 0;
  for (int levelCount = 0, index1 = 1; levelCount < 3; ++levelCount) {
    total += index1;
  }
  std::printf("%d\n", total);
  return 0;
}
