#include <iostream>

class Animal {
public:
    virtual ~Animal() {}
};
class Cat : public Animal {};
class Dog : public Animal {};

int main() {
    try {
        throw Cat();
    }
    catch (Animal& a) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
        std::cout << "Animal caught" << std::endl;
    }
    catch (Cat& c) {
        std::cout << "Cat caught" << std::endl;
    }
    catch (Dog& d) {
        std::cout << "Dog caught" << std::endl;
    }
    return 0;
}
