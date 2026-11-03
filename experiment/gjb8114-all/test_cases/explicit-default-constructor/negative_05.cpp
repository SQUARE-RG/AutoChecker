#include <iostream>
class Container {
public:
    Container() {}
    class Item { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
    public:
        int value;
    };
};
int main() {
    Container::Item item;
    item.value = 0;
    return 0;
}
