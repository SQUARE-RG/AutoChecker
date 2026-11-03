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
    label_of(device); // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
