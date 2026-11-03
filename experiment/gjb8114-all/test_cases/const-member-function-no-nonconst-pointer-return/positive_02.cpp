class IntHolder {
public:
    explicit IntHolder(int* ptr) : ptr_(ptr) {}

    const int& get() const {
        return *ptr_;
    }

private:
    int* ptr_;
};

int main() {
    int value = 3;
    IntHolder holder(&value);
    const int& observed = holder.get();
    return observed == 3 ? 0 : 1;
}
