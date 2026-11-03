#include <initializer_list>

class IntList {
public:
    explicit IntList(std::initializer_list<int> values) : size_(static_cast<int>(values.size())) {
        int i = 0;
        for (int v : values) {
            if (i < 3) data_[i] = v;
            ++i;
        }
    }
    int size() const { return size_; }
private:
    int data_[3];
    int size_;
};

int main() {
    IntList list{1, 2, 3};
    return list.size();
}
