#include <functional>
#include <string>

struct Device
{
    std::string name;

    std::string label() const
    {
        return name;
    }
};

int main()
{
    Device device{"router"};
    auto label_of = std::mem_fn(&Device::label);
    (void)label_of(device);
    return 0;
}
