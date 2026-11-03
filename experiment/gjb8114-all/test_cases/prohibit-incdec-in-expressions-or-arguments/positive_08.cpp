#include <iostream>

int identity(int value) {
    return value;
}

int main() {
    int x = 1;
    bool flag = true;
    int selected = flag ? x : 0;
    ++x;
    int result = identity(flag ? x : 0);
    std::cout << selected << " " << result << std::endl;
    return 0;
}
