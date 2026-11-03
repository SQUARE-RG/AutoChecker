#include <cstdlib>

int fun(int a, int b);

int main() {
    if (nullptr == &fun) {
        return -1;
    }
    return 0;
}

int fun(int a, int b) {
    return a - b;
}
