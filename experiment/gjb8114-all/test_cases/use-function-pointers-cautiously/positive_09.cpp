enum class Operation { Add, Multiply };

template <Operation Op>
int compute(int left, int right) {
    if constexpr (Op == Operation::Add) {
        return left + right;
    } else {
        return left * right;
    }
}

int main() {
    return compute<Operation::Add>(3, 4);
}
