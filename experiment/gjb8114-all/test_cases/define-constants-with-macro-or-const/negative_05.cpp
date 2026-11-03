#include <iostream>

int totalAnnualInterest(int monthlyInterest) {
  int total = 0;
  for (int month = 0; month < 12; ++month) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
    total += monthlyInterest;
  }
  return total;
}

int main() {
  std::cout << totalAnnualInterest(10) << '\n';
  return 0;
}
