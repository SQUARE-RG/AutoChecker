#include <vector>

int main() {
  const std::vector<int> values{1, 2, 3};
  return values.size() == 3 ? 0 : 1;
}
