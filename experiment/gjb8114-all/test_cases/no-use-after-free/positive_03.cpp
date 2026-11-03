#include <iostream>

void release(int*& p)
{
    delete p;
    p = nullptr;
}

int main()
{
    int* value = new int(42);
    int before = *value;
    std::cout << before << '\n';
    release(value);
    if (value == nullptr)
    {
        std::cout << "released\n";
    }
    return 0;
}
