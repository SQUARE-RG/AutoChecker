#include <iostream>

class Record {
public:
    Record() : id_(0), value_(0) {}
    Record(const Record& other) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
        id_ = other.id_;
    }
    int id() const { return id_; }
    int value() const { return value_; }
private:
    int id_;
    int value_;
};

int main() {
    Record original;
    Record duplicate(original);
    std::cout << duplicate.id() << '\n';
    return 0;
}
