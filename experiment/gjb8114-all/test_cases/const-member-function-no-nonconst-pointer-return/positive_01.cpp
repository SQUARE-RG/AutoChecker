class IntHolder {
public:
    explicit IntHolder(int* ptr) : ptr_(ptr) {}

    const int* get() const {
        return ptr_;
    }

private:
    int* ptr_;
};

int main() {
    int values[2] = {1, 2};
    IntHolder holder(values);
    const int* observed = holder.get();
    return observed[0] == 1 ? 0 : 1;
}
