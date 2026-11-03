#include <iostream>
#include <vector>

int main() {
    std::vector<int*> values;
    for (int i = 0; i < 4; ++i) {
        values.push_back(new int(i * 10));
    }
    int sum = 0;
    for (int* value : values) {
        sum += *value;
        delete value;
    }
    values.clear();
    std::cout << sum << std::endl;
    return 0;
}
