#include <iostream>
class Base {
public:
    Base() : value_(0) {}
    int value() const { return value_; }
private:
    int value_;
};
class Middle : public Base {
public:
    Middle() : Base(), middle_(1) {}
    int middle_value() const { return middle_; }
private:
    int middle_;
};
class Leaf : public Middle {
public:
    Leaf() : Middle(), leaf_(2) {}
    int leaf_value() const { return leaf_; }
private:
    int leaf_;
};
int main() {
    Leaf leaf;
    try {
        throw leaf;
    }
    catch (const Leaf& l) {
        std::cout << l.leaf_value() << std::endl;
    }
    catch (const Middle& m) {
        std::cout << m.middle_value() << std::endl;
    }
    catch (const Base& b) {
        std::cout << b.value() << std::endl;
    }
    return 0;
}
