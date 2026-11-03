template <typename T>
struct Box {
    T value;
};

int main() {
    Box<int> box{42};
    return box.value;
}
