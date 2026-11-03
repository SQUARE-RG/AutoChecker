#include <vector>

int process(const std::vector<int>& values) {
  int result = 0;
  for (int i = 0; i < static_cast<int>(values.size()); ++i) {
    if (values[i] == 0) {
      break;
    }
    result += values[i];
  }
  result += 10;
  return result;
}
