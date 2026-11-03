#include <iostream>

int main() {
    int sum = 0;
    for (int i = 1; i <= 10; ++i) {
        sum += i;
    } /* 结束累加循环 */

    if (sum > 0) {
        std::cout << sum << std::endl;
    } /* 结束条件分支 */

    return 0;
}
