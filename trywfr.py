from wfrcwflib.workflow import (
    Workflow, Step,
    PositionalArgument, OptionalArgument,
    InputConnector, OutputConnector,
    )
from wfrcwflib.file import (
    SuffixedFiletype, SuffixedFiletypeBundle, FiletypeRegistry,
    )

x = Step("say hello", "echo")
x.args.append(PositionalArgument("hello"))
x.args.append(PositionalArgument("world"))
print(x)

x2 = Step("read_file", "cat")
x2.args.append(PositionalArgument(InputConnector("f", ".txt")))
print(x2)
print(list(x2.inputs))

c1 = Step("copy_1", "cp")
c1.args.append(PositionalArgument(InputConnector("source", ".toml")))
c1.args.append(PositionalArgument(OutputConnector("dest", ".txt")))

c2 = Step("copy_2", "cp")
c2.args.append(PositionalArgument(InputConnector("source", ".txt")))
c2.args.append(PositionalArgument(OutputConnector("dest", ".config")))

w = Workflow(c1)
print(list(w.inputs))
print(list(w.outputs))

w.add_step(c2, {"source": ("copy_1", "dest")})
print("Connections in:", w.connections_in)
print("Inputs:", list(w.inputs))
print("Connections out:", w.connections_out)      
print("Outputs:", list(w.outputs))

print(w.dag)
print(list(w.edges))


csv_filetype = SuffixedFiletype("csv", ".csv")
fasta_filetype = SuffixedFiletype("fasta", ".fasta", [".fna", ".fa"])
fastq_r1 = SuffixedFiletype("r1", "_R1.fastq")
fastq_r2 = SuffixedFiletype("r2", "_R2.fastq")
paired_fastq_filetype = SuffixedFiletypeBundle("paired-fastq", (fastq_r1, fastq_r2))

registry = FiletypeRegistry()
registry.register(csv_filetype)
registry.register(fasta_filetype)
registry.register(paired_fastq_filetype)
print(registry["fasta"])
print(registry["paired-fastq"])

#input_fp = Path("pyproject.toml")
#p = Project(w, {}, {("copy_1", "source"): input_fp}, "myoutput")

# step copy_1
#   cp
#   {input source toml}
#   {output dest txt}

# step copy_2
#   cp
#   {input source txt}
#   {output dest config}

# workflow double_copy
#   copy_1 dest -> copy_2 source

# step blastn_genes
#   blastn
#   -db {input db blastndb}
#   -in {input seqs fasta}
#   -evalue 1e-5

# configure blastn_genes
#   -evalue 1e-3

#try:
#    x2.run()
#except Exception as e:
#    print(e)
#x2.set_input("f", "pyproject.toml")
#print(x2.inputs)
#print(x2.argv)
#x2.run()
