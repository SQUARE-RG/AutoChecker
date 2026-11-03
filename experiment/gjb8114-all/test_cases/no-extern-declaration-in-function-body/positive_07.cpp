int global_value = 0;

int main() {
    auto read_global = []() {
        return global_value;
    };
    return read_global();
}
