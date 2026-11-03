#include <iostream>

int classify(int value) {
  int result = 0;
  switch (value) {
    case 1:
      result = 10;
      break;
    case 2:
      result = 20;
      break;
    default:
      result = -1;
      break;
  }
  return result;
}

int main() {
  std::cout << classify(1) << ' ' << classify(2) << ' ' << classify(3) << '\n';
  return 0;
}
