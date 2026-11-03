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
    catch (Cat& c) {
        std::cout << "Cat caught" << std::endl;
    }
    catch (Dog& d) {
        std::cout << "Dog caught" << std::endl;
    }
    catch (Animal& a) {
        std::cout << "Animal caught" << std::endl;
    }
    return 0;
}
