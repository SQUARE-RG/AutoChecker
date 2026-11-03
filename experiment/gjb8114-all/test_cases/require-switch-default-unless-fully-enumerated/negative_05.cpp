enum class Opcode : int { Add = 1, Sub = 3, Mul = 5 };

int compute(Opcode op)
{
    int result = 0;
    switch (op) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
        case Opcode::Add:
        case Opcode::Sub:
            result = 1;
            break;
    }
    return result;
}

int main()
{
    return compute(Opcode::Add);
}
