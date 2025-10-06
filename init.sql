CREATE TABLE IF NOT EXISTS produtos (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(80) NOT NULL,
  preco NUMERIC(10,2) NOT NULL
);

INSERT INTO produtos (nome, preco) VALUES 
  ('Notebook Dell Inspiron', 2500.00),
  ('Mouse Logitech', 45.90),
  ('Teclado Mecânico', 120.50),
  ('Monitor 24"', 800.00),
  ('Webcam HD', 150.75)
ON CONFLICT DO NOTHING;

SELECT 'Tabela produtos criada e populada com sucesso!' as status;
