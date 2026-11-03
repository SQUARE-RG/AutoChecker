enum class Opcode : int { Add = 1, Sub = 3, Mul = 5 };

int compute(Opcode op)
{
    int result = 0;
    switch (op) {
        case Opcode::Add:
        case Opcode::Sub:
            result = 1;
            break;
        case Opcode::Mul:
            result = 2;
            break;
    }
    return result;
}

int main()
{
    return compute(Opcode::Add);
}
