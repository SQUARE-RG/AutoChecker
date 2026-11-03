struct PointerHolder {
    int* ptr;

    explicit PointerHolder(int* p)
        : ptr(p) {}
};

int main() {
    int value = 5;
    PointerHolder holder{&value};
    return holder.ptr == &value ? 0 : 1;
}
