#include <cstddef>

class ArrayHolder {
public:
    void update(int (&values)[4])
    {
        for (std::size_t i = 0; i < 4; ++i) {
            values[i] += 1;
        }
    }
};

int main() {
    int data[4] = {0, 1, 2, 3};
    ArrayHolder holder;
    holder.update(data);
    return 0;
}
