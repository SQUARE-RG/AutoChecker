#include <iostream>
#include <memory>

int main()
{
    std::unique_ptr<int> owner(new int(7));
    int* raw = owner.get();
    int value = *raw;
    std::cout << value << '\n';
    raw = nullptr;
    owner.reset();
    return 0;
}
