<script lang="ts">
	import '$lib/styles/layout.css';
	import { FileText, Camera, Upload } from '@lucide/svelte';

	interface Props {
		/** Supported formats */
		formats: string[];
		/** Max size in MB*/
		maxSize: number;
		/** Title of bin*/
		title: string;
	}

	const { formats, maxSize, title }: Props = $props();

	let isDraggingFile = $state(false);
	let files: FileList | null = $state(null);
	let fileInput: HTMLInputElement;

	const handleDragOver = (event: DragEvent) => {
		event.preventDefault();
		if (event.dataTransfer && event.dataTransfer.types.includes('Files')) {
			isDraggingFile = true;
		}
	};

	const handleDragLeave = (event: DragEvent) => {
		if (event.dataTransfer && event.dataTransfer.types.includes('Files')) {
			isDraggingFile = false;
		}
	};

	const handleDrop = (event: DragEvent) => {
		event.preventDefault();
		isDraggingFile = false;
		if (event.dataTransfer) {
			const files = event.dataTransfer.files;
			console.log('Dropped files:', files);
		}
	};

	const handleFileSelect = (event: Event) => {
		const target = event.target as HTMLInputElement;
		if (target.files) {
			console.log('Selected files:', target.files);
		}
	};
</script>

<div
	role="region"
	ondragover={handleDragOver}
	ondragleave={handleDragLeave}
	ondrop={handleDrop}
	class={`rounded-xl border-2 border-dashed bg-white p-12 shadow-sm transition-colors ${
		isDraggingFile ? 'border-forest-green-500 bg-blue-50' : 'border-gray-300'
	}`}
>
	<div class="text-center">
		<Upload class="mx-auto mb-4 h-16 w-16 text-gray-400" />
		<h3 class="mb-2 text-xl font-semibold text-gray-900">{title}</h3>
		<p class="mb-6 text-gray-600">Drag and drop or click to select a file</p>

		<div class="flex flex-col justify-center gap-3 sm:flex-row">
			<button
				onclick={() => fileInput.click()}
				class="inline-flex items-center gap-2 rounded-lg bg-forest-green-600 px-6 py-3 text-white transition-colors hover:bg-forest-green-700"
			>
				<FileText class="h-5 w-5" />
				Choose File
			</button>
			<button
				//onclick={()} <-- TODO: Access webcam and capture photo
				class="inline-flex items-center gap-2 rounded-lg bg-gray-100 px-6 py-3 text-gray-700 transition-colors hover:bg-gray-200"
			>
				<Camera class="h-5 w-5" />
				Take Photo
			</button>
		</div>

		<input
			bind:files
			bind:this={fileInput}
			type="file"
			accept={formats.map((e) => 'image/' + e).join(', ')}
			onchange={handleFileSelect}
			class="hidden"
		/>

		<p class="mt-6 text-sm text-gray-500">
			Supports: {formats.map((e) => e.toUpperCase()).join(', ')} • Max size: {maxSize}MB
		</p>
	</div>
</div>
