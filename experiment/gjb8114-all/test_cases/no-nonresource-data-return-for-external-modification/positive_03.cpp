#include <iostream>

class IntArray {
public:
    IntArray() : values{1, 2, 3} {}

    const int* data() const {
        return values;
    }

private:
    int values[3];
};

int main() {
    IntArray arr;
    const int* data = arr.data();
    int first = data[0];
    std::cout << first << std::endl;
    return 0;
}
