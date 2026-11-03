#include <initializer_list>

class IntList { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    IntList(std::initializer_list<int> values);
    int sum() const;
private:
    int data_[4];
    int count_;
};

IntList::IntList(std::initializer_list<int> values) : data_{}, count_(0) {
    for (int v : values) {
        if (count_ < 4) {
            data_[count_++] = v;
        }
    }
}

int IntList::sum() const {
    int total = 0;
    for (int i = 0; i < count_; ++i) {
        total += data_[i];
    }
    return total;
}

int main() {
    IntList list{1, 2, 3};
    return list.sum();
}
