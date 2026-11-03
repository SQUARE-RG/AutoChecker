#include <iostream>
class Container {
public:
    Container() {}
    class Item {
    public:
        Item() {}
        int value;
    };
};
int main() {
    Container c;
    Container::Item item;
    item.value = 1;
    (void)c;
    return 0;
}
