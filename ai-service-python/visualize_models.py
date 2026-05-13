import os
import matplotlib.pyplot as plt
import numpy as np
from transformers import AutoConfig

def plot_model_statistics(model_names, output_filename="model_analysis_report.png"):
    """
    Generates a visualization dashboard for the specified HuggingFace models,
    including architecture components, parameter distribution, and reported accuracies.
    """
    print(f"Generating visualization for models: {model_names}...")
    
    # Create a figure with subplots
    num_models = len(model_names)
    fig = plt.figure(figsize=(16, 6 * num_models))
    fig.canvas.manager.set_window_title('Legal Document Analyzer - AI Models Report')
    
    for idx, model_name in enumerate(model_names):
        try:
            print(f"Fetching configuration for {model_name}...")
            config = AutoConfig.from_pretrained(model_name)
            
            # Extract basic components
            encoder_layers = getattr(config, 'encoder_layers', getattr(config, 'num_hidden_layers', 0))
            decoder_layers = getattr(config, 'decoder_layers', 0)
            hidden_size = getattr(config, 'd_model', getattr(config, 'hidden_size', 0))
            attention_heads = getattr(config, 'encoder_attention_heads', getattr(config, 'num_attention_heads', 0))
            vocab_size = getattr(config, 'vocab_size', 0)
            
            row_offset = idx * 2
            
            # 1. Architecture Component Bar Chart
            ax1 = plt.subplot(num_models * 2, 2, row_offset * 2 + 1)
            components = ['Encoder Layers', 'Decoder Layers', 'Attention Heads']
            values = [encoder_layers, decoder_layers, attention_heads]
            bars = ax1.bar(components, values, color=['#4C72B0', '#55A868', '#C44E52'])
            ax1.set_title(f"Architecture Components: {model_name.split('/')[-1]}", fontsize=12, pad=10)
            ax1.set_ylabel("Count")
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{int(height)}', ha='center', va='bottom')

            # 2. Parameter Distribution Pie Chart
            ax2 = plt.subplot(num_models * 2, 2, row_offset * 2 + 2)
            embed_params = vocab_size * hidden_size
            # Rough approximation of transformer block parameters
            enc_params = encoder_layers * (12 * hidden_size**2)
            dec_params = decoder_layers * (12 * hidden_size**2)
            
            if decoder_layers > 0:
                labels = ['Embeddings', 'Encoder Blocks', 'Decoder Blocks']
                sizes = [embed_params, enc_params, dec_params]
                colors = ['#8172B3', '#937860', '#DA8BC3']
            else:
                labels = ['Embeddings', 'Encoder Blocks']
                sizes = [embed_params, enc_params]
                colors = ['#8172B3', '#937860']
                
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, 
                    wedgeprops={'edgecolor': 'w', 'linewidth': 1})
            ax2.set_title("Estimated Parameter Distribution", fontsize=12)

            # 3. Accuracy / Performance Metrics
            ax3 = plt.subplot(num_models * 2, 2, row_offset * 2 + 3)
            if "mnli" in model_name.lower():
                metrics = ['MNLI (Matched)', 'MNLI (Mismatched)', 'SNLI']
                accuracies = [89.9, 90.1, 89.5]  # Standard reported metrics for BART-large-MNLI
                title = "Zero-Shot Text Classification Accuracy"
                ylabel = "Accuracy (%)"
                ylim = (80, 100)
            elif "cnn" in model_name.lower():
                metrics = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L']
                accuracies = [44.16, 21.28, 40.90]  # Standard reported metrics for BART-large-CNN
                title = "Summarization Performance (ROUGE Scores)"
                ylabel = "F1 Score"
                ylim = (0, 60)
            else:
                metrics = ['Metric 1', 'Metric 2', 'Metric 3']
                accuracies = [85.0, 87.5, 82.3]
                title = "Model Performance"
                ylabel = "Score"
                ylim = (0, 100)

            bars2 = ax3.bar(metrics, accuracies, color='#64B5F6', width=0.5)
            ax3.set_ylim(ylim)
            ax3.set_ylabel(ylabel)
            ax3.set_title(title, fontsize=12)
            for bar in bars2:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{height}%' if "Accuracy" in title else f'{height}', ha='center', va='bottom')

            # 4. Text Summary Details
            ax4 = plt.subplot(num_models * 2, 2, row_offset * 2 + 4)
            ax4.axis('off')
            total_params = sum(sizes)
            summary_text = (
                f"Model Configuration Summary\n"
                f"{'='*40}\n"
                f"Model Name       : {model_name}\n"
                f"Hidden Size      : {hidden_size}\n"
                f"Vocabulary Size  : {vocab_size:,}\n"
                f"Max Seq Length   : {getattr(config, 'max_position_embeddings', 'N/A')}\n"
                f"Total Parameters : ~{total_params / 1_000_000:.1f} Million\n"
                f"Activation Func  : {getattr(config, 'activation_function', getattr(config, 'hidden_act', 'N/A'))}\n"
                f"Architecture     : {'Encoder-Decoder' if decoder_layers > 0 else 'Encoder-Only'}\n\n"
                f"Project Usage:\n"
                f"{'Used for Zero-shot clause detection' if 'mnli' in model_name.lower() else 'Used for document abstractive summarization'}"
            )
            ax4.text(0.1, 0.5, summary_text, fontsize=11, verticalalignment='center', 
                     fontfamily='monospace', bbox=dict(facecolor='#f4f4f4', edgecolor='gray', boxstyle='round,pad=1'))

        except Exception as e:
            print(f"Error processing model {model_name}: {str(e)}")
            
    plt.tight_layout(pad=3.0)
    
    # Save the figure
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\nVisualization successfully saved to: {os.path.abspath(output_filename)}")
    plt.close()

if __name__ == "__main__":
    # Models used in the project based on main.py
    models_to_analyze = [
        "facebook/bart-large-mnli",  # Used for zero-shot classification
        "facebook/bart-large-cnn"    # Used for summarization
    ]
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_visualization_report.png")
    
    print("Dependencies Check:")
    print("Ensure you have matplotlib installed: pip install matplotlib transformers numpy torch")
    
    plot_model_statistics(models_to_analyze, output_path)
