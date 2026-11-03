#include <array>
#include <numeric>
#include <iostream>
int gValue = 5;
class Foo {
public:
    Foo(const std::array<int, 3>& values) {
        a = std::accumulate(values.begin(), values.end(), 0);
    }
private:
    int a;
};
int main() {
    std::array<int, 3> values = {gValue, 2, 3};
    Foo f(values);
    return 0;
}
