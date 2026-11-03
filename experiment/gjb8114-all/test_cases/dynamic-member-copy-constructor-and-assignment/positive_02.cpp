#include <algorithm>
#include <cstring>
#include <utility>

class Record {
public:
    Record(int n, const char* label)
        : count_(n), values_(new int[n]), label_(new char[32]) {
        std::fill(values_, values_ + count_, 0);
        std::strncpy(label_, label, 31);
        label_[31] = '\0';
    }
    Record(const Record& other)
        : count_(other.count_), values_(new int[other.count_]), label_(new char[32]) {
        std::copy(other.values_, other.values_ + count_, values_);
        std::strncpy(label_, other.label_, 31);
        label_[31] = '\0';
    }
    Record& operator=(const Record& other) {
        if (this != &other) {
            Record temp(other);
            swap(temp);
        }
        return *this;
    }
    ~Record() {
        delete[] values_;
        delete[] label_;
    }
private:
    void swap(Record& other) noexcept {
        std::swap(count_, other.count_);
        std::swap(values_, other.values_);
        std::swap(label_, other.label_);
    }
    int count_;
    int* values_;
    char* label_;
};

int main() {
    Record r1(3, "abc");
    Record r2(r1);
    r1 = r2;
    return 0;
}
