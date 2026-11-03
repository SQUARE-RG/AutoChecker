bool is_not_found(int code) {
  switch (code) {
    case 404: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
      return true;
    default:
      return false;
  }
}

int main(int argc, char** argv) {
  return is_not_found(argc);
}
