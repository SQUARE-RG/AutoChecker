#include <iostream>

const int kMonthsInYear = 12;

int totalAnnualInterest(int monthlyInterest) {
  int total = 0;
  for (int month = 0; month < kMonthsInYear; ++month) {
    total += monthlyInterest;
  }
  return total;
}

int main() {
  std::cout << totalAnnualInterest(10) << '\n';
  return 0;
}
