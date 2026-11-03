#include <memory>

int main()
{
    auto sp = std::make_shared<int>(42);
    int *raw = sp.get();
    int y = *raw;
    sp.reset();

    return y;
}
